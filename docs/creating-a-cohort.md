# Creating a cohort

1. Choose a stable ID such as `github-starter-2027-01`.
2. Create `cohorts/<cohort-id>/cohort.yml` from the template. Set real dates and reference every scheduled course session.
3. Create `enrollment.yml` with approved canonical student IDs only.
4. Validate before merging.

```bash
python scripts/validate_data.py
python scripts/generate_report.py --cohort github-starter-2027-01
```

Keep the course reusable: dates belong in the cohort; relative due timing belongs in assignment definitions. Change status from `planned` to `active`, then `completed` and `archived` through reviewed pull requests.
