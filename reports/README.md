# Reports

Run `python scripts/generate_report.py` after a real cohort is configured. Generated reports are derived, idempotent views of canonical records and should not be edited by hand.

The repository does not publish reports to GitHub Pages by default. Public Pages cannot protect private grades or instructor notes. The workflow uploads reports as a restricted Actions artifact; an instructor can publish a deliberately redacted view later.
