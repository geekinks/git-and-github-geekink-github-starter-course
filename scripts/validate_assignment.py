#!/usr/bin/env python3
"""Validate one untrusted submission without executing student code."""
import argparse
from training_core import ROOT, TrainingDataError, load_catalog, load_yaml, safe_path, validate, validate_assignment_artifacts

parser = argparse.ArgumentParser()
parser.add_argument("submission", help="Repository-relative submission YAML path")
args = parser.parse_args()

try:
    submission_path = safe_path(ROOT, args.submission, must_exist=True)
    submission = load_yaml(submission_path)
    errors = validate(submission, "submission", submission_path)
    catalog, catalog_errors = load_catalog()
    errors.extend(catalog_errors)
    assignment = catalog.assignments.get(submission.get("assignment_id"))
    if not assignment:
        errors.append("Unknown assignment_id")
    elif submission.get("status") not in {"submitted", "changes_requested"}:
        errors.append("Student-authored submissions may only use submitted or changes_requested status; instructors approve separately")
    if assignment:
        errors.extend(validate_assignment_artifacts(submission, assignment, ROOT))
except TrainingDataError as exc:
    errors = [str(exc)]

if errors:
    print("Submission validation failed:")
    for error in errors: print(f"- {error}")
    raise SystemExit(1)
print(f"Submission {submission['submission_id']} passed automated checks and still requires instructor review.")
