# Student guide

## Register

Open **Issues → New issue → Student registration**. Enter only your GitHub username, chosen display name, and the cohort ID provided by the instructor. The instructor checks the account and assigns your stable student ID. Never post passwords, tokens, email, phone, address, or identity documents.

## Complete and submit work

Read the relevant assignment YAML and its human-readable `instructions`, `submission.requirements`, and due date supplied by the cohort. Submission methods vary: a file or pull request, an issue response, or links to an external repository and Pages site.

When a structured record is required, copy `templates/submission.yml`, use a unique lowercase submission ID, set status to `submitted`, add only repository-relative paths and HTTPS evidence URLs, and open a pull request. Run:

```bash
python scripts/validate_assignment.py tracking/submissions/your-submission.yml
```

Fix each printed error and push again. “Passed automated checks” means the structure and configured machine checks passed. Wait for instructor feedback before treating the work as approved or complete.
