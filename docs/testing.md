# Testing

Run the same checks as continuous integration:

```bash
python -m pip install -r requirements.txt
python scripts/validate_data.py
python -m unittest discover -s tests -v
```

Tests cover valid and invalid courses and students, incorrect submission metadata, unsafe and missing paths, incomplete work, attendance, completion, latest-update conflict handling, idempotent calculation, empty cohorts, invalid cohort references, and duplicate student IDs. Fixtures live only in temporary directories and never modify production records.

To exercise a real workflow locally, install `act` and run `act pull_request` with a representative event payload. Local emulation does not prove GitHub token permissions, Code Owner enforcement, issue-form rendering, scheduled events, or artifact retention; verify those once in a protected test repository.
