"""Shared, side-effect-free training data loader and progress calculator."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "config" / "schemas"
APPROVED = {"approved", "completed"}
SUBMITTED = {"submitted", "automated_checks_passed", "awaiting_instructor_review", "changes_requested", "approved", "completed"}


class TrainingDataError(ValueError):
    pass


def safe_path(root: Path, value: str | Path, *, must_exist: bool = False) -> Path:
    candidate = Path(value)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise TrainingDataError(f"Unsafe path: {value!s}")
    resolved = (root / candidate).resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError as exc:
        raise TrainingDataError(f"Path escapes repository: {value!s}") from exc
    if must_exist and not resolved.exists():
        raise TrainingDataError(f"Required path does not exist: {value!s}")
    return resolved


def load_yaml(path: Path) -> Any:
    try:
        with path.open(encoding="utf-8") as stream:
            value = yaml.safe_load(stream)
    except (OSError, yaml.YAMLError) as exc:
        raise TrainingDataError(f"Cannot read {path}: {exc}") from exc
    if value is None:
        raise TrainingDataError(f"{path} is empty")
    return value


def schema(name: str) -> dict[str, Any]:
    with (SCHEMAS / f"{name}.schema.json").open(encoding="utf-8") as stream:
        return json.load(stream)


def validate(instance: Any, schema_name: str, source: Path) -> list[str]:
    validator = Draft202012Validator(schema(schema_name), format_checker=FormatChecker())
    errors = []
    for error in sorted(validator.iter_errors(instance), key=lambda item: list(item.path)):
        location = ".".join(str(part) for part in error.path) or "<root>"
        errors.append(f"{source}: {location}: {error.message}")
    return errors


def yaml_files(directory: Path) -> list[Path]:
    if not directory.exists():
        return []
    return sorted([*directory.glob("*.yml"), *directory.glob("*.yaml")])


@dataclass(frozen=True)
class Catalog:
    students: dict[str, dict[str, Any]]
    courses: dict[str, dict[str, Any]]
    sessions: dict[str, dict[str, Any]]
    assignments: dict[str, dict[str, Any]]
    cohorts: dict[str, dict[str, Any]]
    enrollment: dict[str, list[str]]
    attendance: list[dict[str, Any]]
    submissions: list[dict[str, Any]]
    assessments: list[dict[str, Any]]
    completions: list[dict[str, Any]]


def _unique(records: Iterable[dict[str, Any]], key: str, errors: list[str]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for record in records:
        if not isinstance(record, dict):
            errors.append(f"Record for {key} must be an object")
            continue
        record_id = record.get(key)
        if not isinstance(record_id, str):
            continue
        if record_id in result:
            errors.append(f"Duplicate {key}: {record_id}")
        result[record_id] = record
    return result


def load_catalog(root: Path = ROOT) -> tuple[Catalog, list[str]]:
    errors: list[str] = []

    student_path = root / "students" / "students.yml"
    student_doc = load_yaml(student_path)
    if not isinstance(student_doc, dict) or not isinstance(student_doc.get("students"), list):
        raise TrainingDataError(f"{student_path} must contain a students list")
    for item in student_doc["students"]:
        errors.extend(validate(item, "student", student_path))
    students = _unique(student_doc["students"], "student_id", errors)
    usernames: set[str] = set()
    for item in student_doc["students"]:
        username = item.get("github_username", "").lower()
        if username in usernames:
            errors.append(f"Duplicate GitHub username: {item.get('github_username')}")
        usernames.add(username)

    course_records: list[dict[str, Any]] = []
    session_records: list[dict[str, Any]] = []
    assignment_records: list[dict[str, Any]] = []
    for course_file in sorted((root / "courses").glob("*/course.yml")):
        record = load_yaml(course_file)
        errors.extend(validate(record, "course", course_file))
        course_records.append(record)
        for path in yaml_files(course_file.parent / "sessions"):
            item = load_yaml(path); errors.extend(validate(item, "session", path)); session_records.append(item)
        for path in yaml_files(course_file.parent / "assignments"):
            item = load_yaml(path); errors.extend(validate(item, "assignment", path)); assignment_records.append(item)
    courses = _unique(course_records, "course_id", errors)
    sessions = _unique(session_records, "session_id", errors)
    assignments = _unique(assignment_records, "assignment_id", errors)

    cohort_records: list[dict[str, Any]] = []
    enrollment: dict[str, list[str]] = {}
    for cohort_file in sorted((root / "cohorts").glob("*/cohort.yml")):
        record = load_yaml(cohort_file); errors.extend(validate(record, "cohort", cohort_file)); cohort_records.append(record)
        enrollment_file = cohort_file.parent / "enrollment.yml"
        enrollment_doc = load_yaml(enrollment_file)
        ids = enrollment_doc.get("student_ids") if isinstance(enrollment_doc, dict) else None
        if not isinstance(ids, list) or any(not isinstance(item, str) for item in ids):
            errors.append(f"{enrollment_file}: student_ids must be a list of strings")
            ids = []
        if len(ids) != len(set(ids)):
            errors.append(f"{enrollment_file}: duplicate student enrollment")
        if isinstance(record.get("cohort_id"), str):
            enrollment[record["cohort_id"]] = ids
    cohorts = _unique(cohort_records, "cohort_id", errors)

    attendance: list[dict[str, Any]] = []
    for path in yaml_files(root / "tracking" / "attendance"):
        item = load_yaml(path); errors.extend(validate(item, "attendance", path)); attendance.append(item)
    submissions: list[dict[str, Any]] = []
    for path in yaml_files(root / "tracking" / "submissions"):
        item = load_yaml(path); errors.extend(validate(item, "submission", path)); submissions.append(item)
    assessments: list[dict[str, Any]] = []
    for path in yaml_files(root / "tracking" / "assessments"):
        item = load_yaml(path); errors.extend(validate(item, "assessment", path)); assessments.append(item)
    completions: list[dict[str, Any]] = []
    for path in yaml_files(root / "tracking" / "completions"):
        item = load_yaml(path); errors.extend(validate(item, "completion", path)); completions.append(item)

    _unique(submissions, "submission_id", errors)
    _unique(attendance, "attendance_id", errors)
    _unique(assessments, "assessment_id", errors)
    _unique(completions, "completion_id", errors)

    for course in courses.values():
        course_id = course.get("course_id", "<invalid>")
        for session_id in course.get("session_ids", []):
            if session_id not in sessions or sessions[session_id].get("course_id") != course_id:
                errors.append(f"Course {course_id} has invalid session reference: {session_id}")
        for assignment_id in course.get("assignment_ids", []):
            if assignment_id not in assignments or assignments[assignment_id].get("course_id") != course_id:
                errors.append(f"Course {course_id} has invalid assignment reference: {assignment_id}")
        completion = course.get("completion", {}) if isinstance(course.get("completion"), dict) else {}
        unknown_required = set(completion.get("required_assignment_ids", [])) - set(course.get("assignment_ids", []))
        if unknown_required:
            errors.append(f"Course {course_id} completion references unknown assignments: {sorted(unknown_required)}")
    for assignment in assignments.values():
        if assignment.get("session_id") not in sessions:
            errors.append(f"Assignment {assignment['assignment_id']} has invalid session reference")
    for cohort in cohorts.values():
        if cohort.get("course_id") not in courses:
            errors.append(f"Cohort {cohort['cohort_id']} has invalid course reference")
        if cohort.get("start_date") and cohort.get("end_date") and cohort["start_date"] > cohort["end_date"]:
            errors.append(f"Cohort {cohort['cohort_id']} ends before it starts")
        for scheduled in cohort.get("schedule", []):
            if scheduled["session_id"] not in sessions:
                errors.append(f"Cohort {cohort['cohort_id']} has invalid scheduled session {scheduled['session_id']}")
        for deadline in cohort.get("assignment_deadlines", []):
            if deadline["assignment_id"] not in assignments:
                errors.append(f"Cohort {cohort['cohort_id']} has invalid assignment deadline {deadline['assignment_id']}")
    for cohort_id, ids in enrollment.items():
        for student_id in ids:
            if student_id not in students:
                errors.append(f"Cohort {cohort_id} enrolls unknown student {student_id}")
    for record in submissions:
        if record.get("student_id") not in students: errors.append(f"Submission {record.get('submission_id')} references unknown student")
        if record.get("cohort_id") not in cohorts: errors.append(f"Submission {record.get('submission_id')} references unknown cohort")
        if record.get("assignment_id") not in assignments: errors.append(f"Submission {record.get('submission_id')} references unknown assignment")
        try:
            if record.get("artifact_root"): safe_path(root, record["artifact_root"])
        except TrainingDataError as exc: errors.append(str(exc))
    for record in attendance:
        if record.get("cohort_id") not in cohorts: errors.append(f"Attendance {record.get('attendance_id')} references unknown cohort")
        for entry in record.get("entries", []):
            if entry.get("student_id") not in students: errors.append(f"Attendance {record.get('attendance_id')} references unknown student")
        entry_ids = [entry.get("student_id") for entry in record.get("entries", [])]
        if len(entry_ids) != len(set(entry_ids)): errors.append(f"Attendance {record.get('attendance_id')} has duplicate student entries")
    for record in assessments:
        if record.get("student_id") not in students: errors.append(f"Assessment {record.get('assessment_id')} references unknown student")
        if record.get("cohort_id") not in cohorts: errors.append(f"Assessment {record.get('assessment_id')} references unknown cohort")
    for record in completions:
        if record.get("student_id") not in students: errors.append(f"Completion {record.get('completion_id')} references unknown student")
        if record.get("cohort_id") not in cohorts: errors.append(f"Completion {record.get('completion_id')} references unknown cohort")
        try: safe_path(root, record.get("report_reference", ""))
        except TrainingDataError as exc: errors.append(str(exc))

    return Catalog(students, courses, sessions, assignments, cohorts, enrollment, attendance, submissions, assessments, completions), errors


def validate_assignment_artifacts(submission: dict[str, Any], assignment: dict[str, Any], root: Path) -> list[str]:
    """Apply declarative checks without executing any submitted content."""
    errors: list[str] = []
    try:
        artifact_root = safe_path(root, submission.get("artifact_root", "."))
    except TrainingDataError as exc:
        return [str(exc)]
    for rule in assignment.get("validation", []):
        if rule["type"] == "required_file":
            try: safe_path(artifact_root, rule["path"], must_exist=True)
            except TrainingDataError as exc: errors.append(str(exc))
        elif rule["type"] == "markdown_heading":
            try:
                file_path = safe_path(artifact_root, rule["path"], must_exist=True)
                text = file_path.read_text(encoding="utf-8")
                if not re.search(rf"^#+\s+{re.escape(rule['heading'])}\s*$", text, re.MULTILINE | re.IGNORECASE):
                    errors.append(f"Missing Markdown heading {rule['heading']!r} in {rule['path']}")
            except (TrainingDataError, OSError, UnicodeError) as exc: errors.append(str(exc))
        elif rule["type"] == "url_field":
            value = submission.get("evidence", {}).get(rule["field"], "")
            if not re.fullmatch(r"https://[A-Za-z0-9.-]+(?:/[^\s]*)?", value):
                errors.append(f"evidence.{rule['field']} must be a valid HTTPS URL")
    return errors


def student_progress(catalog: Catalog, cohort_id: str, student_id: str) -> dict[str, Any]:
    cohort = catalog.cohorts[cohort_id]
    course = catalog.courses[cohort["course_id"]]
    required = set(course["completion"]["required_assignment_ids"])
    latest: dict[str, dict[str, Any]] = {}
    for record in catalog.submissions:
        if record["cohort_id"] == cohort_id and record["student_id"] == student_id:
            previous = latest.get(record["assignment_id"])
            if previous is None or record["submitted_at"] >= previous["submitted_at"]:
                latest[record["assignment_id"]] = record
    submitted = {key for key, value in latest.items() if value["status"] in SUBMITTED}
    approved = {key for key, value in latest.items() if value["status"] in APPROVED}
    attendance_entries = [entry for record in catalog.attendance if record["cohort_id"] == cohort_id for entry in record["entries"] if entry["student_id"] == student_id]
    attended = sum(entry["status"] in {"present", "late"} for entry in attendance_entries)
    final_assessments = [item for item in catalog.assessments if item["cohort_id"] == cohort_id and item["student_id"] == student_id and item["assessment_type"] == "final_project"]
    final_passed = any(item["result"] == "passed" and (item["score"] / item["maximum_score"] * 100) >= course["completion"].get("minimum_final_score", 0) for item in final_assessments)
    attendance_ok = attended >= course["completion"]["minimum_attendance_sessions"]
    assignment_ok = required <= approved
    assessment_ok = final_passed or not course["completion"]["final_assessment_required"]
    assignment_ratio = len(required & approved) / len(required) if required else 1
    attendance_target = course["completion"]["minimum_attendance_sessions"]
    attendance_ratio = min(attended / attendance_target, 1) if attendance_target else 1
    components = [assignment_ratio, attendance_ratio] + ([1 if assessment_ok else 0] if course["completion"]["final_assessment_required"] else [])
    return {
        "student_id": student_id, "github_username": catalog.students[student_id]["github_username"],
        "sessions_attended": attended, "assignments_submitted": len(required & submitted), "assignments_approved": len(required & approved),
        "outstanding_assignments": sorted(required - approved), "progress_percentage": round(sum(components) / len(components) * 100),
        "completion_status": "completed" if assignment_ok and attendance_ok and assessment_ok else "in_progress",
    }
