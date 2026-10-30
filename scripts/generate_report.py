#!/usr/bin/env python3
"""Generate deterministic, read-only Markdown and JSON cohort reports."""
import argparse
import json
from pathlib import Path

from training_core import ROOT, load_catalog, student_progress

parser = argparse.ArgumentParser()
parser.add_argument("--cohort", help="Cohort ID; defaults to every cohort")
parser.add_argument("--output", default="reports/generated")
args = parser.parse_args()

catalog, errors = load_catalog()
if errors:
    for error in errors: print(f"- {error}")
    raise SystemExit(1)
cohort_ids = [args.cohort] if args.cohort else sorted(catalog.cohorts)
unknown = set(cohort_ids) - set(catalog.cohorts)
if unknown: raise SystemExit(f"Unknown cohort(s): {sorted(unknown)}")
output = (ROOT / args.output).resolve()
output.relative_to(ROOT)
output.mkdir(parents=True, exist_ok=True)

for cohort_id in cohort_ids:
    cohort = catalog.cohorts[cohort_id]
    course = catalog.courses[cohort["course_id"]]
    students = [student_progress(catalog, cohort_id, student_id) for student_id in catalog.enrollment.get(cohort_id, [])]
    submission_records = [item for item in catalog.submissions if item["cohort_id"] == cohort_id]
    report = {
        "cohort": {"cohort_id": cohort_id, "name": cohort["name"], "course": course["title"], "start_date": cohort["start_date"], "end_date": cohort["end_date"], "enrolled": len(students), "active": sum(catalog.students[item["student_id"]]["status"] == "active" for item in students), "completed": sum(item["completion_status"] == "completed" for item in students)},
        "assignment_overview": {"total_assignments": len(course["assignment_ids"]), "submissions_received": len(submission_records), "automated_checks_passed": sum(item["status"] in {"automated_checks_passed", "awaiting_instructor_review", "approved", "completed"} for item in submission_records), "reviews_pending": sum(item["status"] == "awaiting_instructor_review" for item in submission_records), "changes_requested": sum(item["status"] == "changes_requested" for item in submission_records), "approved": sum(item["status"] in {"approved", "completed"} for item in submission_records)},
        "students": students,
    }
    (output / f"{cohort_id}.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    lines = [f"# {cohort['name']} progress report", "", f"Course: {course['title']}", f"Dates: {cohort['start_date']} to {cohort['end_date']}", f"Enrollment: {len(students)}", "", "| Student ID | GitHub | Attendance | Submitted | Approved | Progress | Status |", "|---|---|---:|---:|---:|---:|---|"]
    lines.extend(f"| {item['student_id']} | @{item['github_username']} | {item['sessions_attended']} | {item['assignments_submitted']} | {item['assignments_approved']} | {item['progress_percentage']}% | {item['completion_status']} |" for item in students)
    lines.extend(["", "## Instructor queue", "", f"- Reviews pending: {report['assignment_overview']['reviews_pending']}", f"- Changes requested: {report['assignment_overview']['changes_requested']}", f"- Sessions without attendance: {len(cohort['schedule']) - len({item['session_id'] for item in catalog.attendance if item['cohort_id'] == cohort_id})}", ""])
    (output / f"{cohort_id}.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Generated {cohort_id} report in {output.relative_to(ROOT)}")
