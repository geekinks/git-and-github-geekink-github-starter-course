#!/usr/bin/env python3
"""Validate every training record and all cross-record references."""
import sys
from training_core import TrainingDataError, load_catalog

try:
    catalog, errors = load_catalog()
except TrainingDataError as exc:
    print(f"ERROR: {exc}")
    raise SystemExit(1)

if errors:
    print("Training data validation failed:")
    for error in errors:
        print(f"- {error}")
    raise SystemExit(1)
print(f"Validated {len(catalog.courses)} course(s), {len(catalog.cohorts)} cohort(s), and {len(catalog.students)} student record(s).")
