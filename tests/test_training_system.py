import copy
import json
import tempfile
import unittest
from pathlib import Path

import yaml

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from training_core import Catalog, TrainingDataError, load_catalog, safe_path, student_progress, validate, validate_assignment_artifacts


def catalog(submissions=None, attendance=None, assessments=None):
    student = {"student_id": "GI-TEST-001", "github_username": "octocat", "display_name": "Test Learner", "status": "active"}
    course = {"course_id": "test-course", "title": "Test", "completion": {"required_assignment_ids": ["a-1", "a-2"], "minimum_attendance_sessions": 2, "final_assessment_required": True, "minimum_final_score": 70}, "assignment_ids": ["a-1", "a-2"]}
    cohort = {"cohort_id": "test-cohort", "course_id": "test-course", "name": "Test", "schedule": [{"session_id": "s-1"}, {"session_id": "s-2"}]}
    return Catalog({"GI-TEST-001": student}, {"test-course": course}, {}, {}, {"test-cohort": cohort}, {"test-cohort": ["GI-TEST-001"]}, attendance or [], submissions or [], assessments or [], [])


class SchemaTests(unittest.TestCase):
    def test_valid_and_invalid_student(self):
        valid = {"student_id": "GI-GH-999", "github_username": "valid-user", "display_name": "Valid", "status": "active"}
        self.assertEqual(validate(valid, "student", Path("student.yml")), [])
        invalid = dict(valid, github_username="space user")
        self.assertTrue(validate(invalid, "student", Path("student.yml")))

    def test_valid_and_invalid_course(self):
        valid = {"course_id": "course-one", "title": "Course", "version": 1, "description": "Description", "session_ids": ["session-01"], "assignment_ids": ["assignment-01"], "completion": {"required_assignment_ids": ["assignment-01"], "minimum_attendance_sessions": 1, "final_assessment_required": False}}
        self.assertEqual(validate(valid, "course", Path("course.yml")), [])
        invalid = copy.deepcopy(valid); invalid["course_id"] = "Unsafe ID"
        self.assertTrue(validate(invalid, "course", Path("course.yml")))

    def test_incorrect_submission_metadata(self):
        bad = {"submission_id": "sub-1", "student_id": "wrong", "cohort_id": "c-1", "assignment_id": "a-1", "submitted_at": "yesterday", "status": "done", "evidence": {}}
        self.assertGreaterEqual(len(validate(bad, "submission", Path("submission.yml"))), 3)


class SafetyTests(unittest.TestCase):
    def test_rejects_malicious_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for value in ("../secret", "/etc/passwd", "ok/../../secret"):
                with self.assertRaises(TrainingDataError): safe_path(root, value)

    def test_missing_required_assignment_file(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(TrainingDataError): safe_path(Path(directory), "README.md", must_exist=True)

    def test_assignment_file_heading_and_url_checks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "work").mkdir()
            (root / "work/README.md").write_text("# Project\n\n## Setup\n", encoding="utf-8")
            assignment = {"validation": [{"type": "required_file", "path": "README.md"}, {"type": "markdown_heading", "path": "README.md", "heading": "Setup"}, {"type": "url_field", "field": "repository_url"}]}
            submission = {"artifact_root": "work", "evidence": {"repository_url": "https://github.com/octocat/example"}}
            self.assertEqual(validate_assignment_artifacts(submission, assignment, root), [])
            submission["evidence"]["repository_url"] = "javascript:alert(1)"
            self.assertTrue(validate_assignment_artifacts(submission, assignment, root))


class ProgressTests(unittest.TestCase):
    def _submission(self, assignment, status, time):
        return {"submission_id": f"sub-{assignment}-{time}", "student_id": "GI-TEST-001", "cohort_id": "test-cohort", "assignment_id": assignment, "submitted_at": time, "status": status, "evidence": {}}

    def test_incomplete_assignment_and_attendance(self):
        data = catalog(submissions=[self._submission("a-1", "approved", "2027-01-01T00:00:00Z")])
        progress = student_progress(data, "test-cohort", "GI-TEST-001")
        self.assertEqual(progress["completion_status"], "in_progress")
        self.assertEqual(progress["outstanding_assignments"], ["a-2"])

    def test_attendance_calculation_and_completion(self):
        submissions = [self._submission("a-1", "approved", "2027-01-01T00:00:00Z"), self._submission("a-2", "completed", "2027-01-02T00:00:00Z")]
        attendance = [{"cohort_id": "test-cohort", "entries": [{"student_id": "GI-TEST-001", "status": "present"}]}, {"cohort_id": "test-cohort", "entries": [{"student_id": "GI-TEST-001", "status": "late"}]}]
        assessments = [{"cohort_id": "test-cohort", "student_id": "GI-TEST-001", "assessment_type": "final_project", "score": 70, "maximum_score": 100, "result": "passed"}]
        progress = student_progress(catalog(submissions, attendance, assessments), "test-cohort", "GI-TEST-001")
        self.assertEqual(progress["sessions_attended"], 2)
        self.assertEqual(progress["progress_percentage"], 100)
        self.assertEqual(progress["completion_status"], "completed")

    def test_latest_submission_wins_and_is_idempotent(self):
        submissions = [self._submission("a-1", "approved", "2027-01-01T00:00:00Z"), self._submission("a-1", "changes_requested", "2027-01-02T00:00:00Z")]
        data = catalog(submissions=submissions)
        first = student_progress(data, "test-cohort", "GI-TEST-001")
        second = student_progress(data, "test-cohort", "GI-TEST-001")
        self.assertEqual(first, second)
        self.assertEqual(first["assignments_approved"], 0)


class CatalogTests(unittest.TestCase):
    def _write(self, path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump(value, sort_keys=False), encoding="utf-8")

    def _fixture(self, root):
        self._write(root / "students/students.yml", {"students": [{"student_id": "GI-TEST-001", "github_username": "octocat", "display_name": "Test", "status": "active"}]})
        self._write(root / "courses/test/course.yml", {"course_id": "test-course", "title": "Test", "version": 1, "description": "Test course", "session_ids": ["session-01"], "assignment_ids": ["assignment-01"], "completion": {"required_assignment_ids": ["assignment-01"], "minimum_attendance_sessions": 1, "final_assessment_required": False}})
        self._write(root / "courses/test/sessions/session.yml", {"session_id": "session-01", "course_id": "test-course", "sequence": 1, "title": "Session", "duration_minutes": 60, "topics": ["Topic"], "objectives": ["Objective"], "resources": []})
        self._write(root / "courses/test/assignments/assignment.yml", {"assignment_id": "assignment-01", "course_id": "test-course", "session_id": "session-01", "title": "Assignment", "instructions": "Do work", "learning_objectives": ["Learn"], "submission": {"method": "file", "requirements": ["File"]}, "validation": [], "maximum_score": 10, "human_review_required": True})

    def test_empty_cohort_collection_is_valid(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); self._fixture(root)
            loaded, errors = load_catalog(root)
            self.assertEqual(errors, [])
            self.assertEqual(loaded.cohorts, {})

    def test_invalid_cohort_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); self._fixture(root)
            self._write(root / "cohorts/test/cohort.yml", {"cohort_id": "test-cohort", "course_id": "missing-course", "name": "Test", "status": "planned", "start_date": "2027-01-01", "end_date": "2027-01-02", "schedule": [{"session_id": "session-01", "date": "2027-01-01", "duration_minutes": 60}]})
            self._write(root / "cohorts/test/enrollment.yml", {"student_ids": []})
            _, errors = load_catalog(root)
            self.assertTrue(any("invalid course reference" in item for item in errors))

    def test_duplicate_student_identifier(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); self._fixture(root)
            duplicate = {"student_id": "GI-TEST-001", "github_username": "other", "display_name": "Other", "status": "active"}
            self._write(root / "students/students.yml", {"students": [{"student_id": "GI-TEST-001", "github_username": "octocat", "display_name": "Test", "status": "active"}, duplicate]})
            _, errors = load_catalog(root)
            self.assertTrue(any("Duplicate student_id" in item for item in errors))

    def test_invalid_course_reports_errors_instead_of_crashing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); self._fixture(root)
            self._write(root / "courses/test/course.yml", {"title": "Missing required fields"})
            _, errors = load_catalog(root)
            self.assertTrue(any("course_id" in item for item in errors))


class RepositorySyntaxTests(unittest.TestCase):
    def test_all_yaml_and_json_files_parse(self):
        root = Path(__file__).resolve().parents[1]
        for path in root.rglob("*.yml"):
            with self.subTest(path=path):
                self.assertIsNotNone(yaml.safe_load(path.read_text(encoding="utf-8")))
        for path in root.rglob("*.json"):
            with self.subTest(path=path):
                json.loads(path.read_text(encoding="utf-8"))

    def test_workflows_have_explicit_permissions_and_triggers(self):
        root = Path(__file__).resolve().parents[1]
        for path in (root / ".github/workflows").glob("*.yml"):
            with self.subTest(path=path):
                workflow = yaml.safe_load(path.read_text(encoding="utf-8"))
                self.assertIn("on", workflow)
                self.assertEqual(workflow.get("permissions"), {"contents": "read"})


if __name__ == "__main__":
    unittest.main()
