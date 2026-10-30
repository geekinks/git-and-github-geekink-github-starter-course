# GeekInk Training Automation System

![GeekInk logo](./logo.png)

This repository is a reusable, GitHub-native training management system. Its first course is the two-week, six-session [Git and GitHub Starter Course](courses/git-and-github-starter/README.md).

The system keeps course definitions, delivery cohorts, canonical student records, submissions, attendance, assessments, automation, and derived reports separate. A passing workflow means only that automated checks passed; instructors remain responsible for attendance, qualitative review, assessment, and completion decisions.

## Quick start

```bash
python -m pip install -r requirements.txt
python scripts/validate_data.py
python -m unittest discover -s tests -v
python scripts/generate_report.py
```

There is intentionally no production cohort yet: the legacy repository does not contain reliable dates or enrollment decisions. An instructor creates one from `templates/cohort.yml` and `templates/enrollment.yml`.

## Student journey

1. Open a Student registration issue with a GitHub username, display name, and instructor-provided cohort ID.
2. Wait for the instructor to validate the GitHub account and add a canonical student ID and cohort enrollment.
3. Attend the session; the instructor records attendance explicitly.
4. Read the assignment in `courses/<course-id>/assignments/` and complete its stated submission method.
5. Add a submission record from `templates/submission.yml` when requested, then open a pull request or submission issue.
6. Fix actionable workflow errors. Passing checks moves work toward human review; it is not approval.
7. Respond to instructor feedback until the assignment is approved.
8. Complete the final project and assessment. The report calculates completion from configured requirements.

## Instructor journey

Use the [instructor guide](docs/instructor-guide.md) for repository setup, courses, cohorts, enrollment, attendance, reviews, assessment, reports, completion, and archiving. Students should start with the [student guide](docs/student-guide.md).

## Repository map

| Path | Purpose |
|---|---|
| `config/` | System settings and JSON Schemas |
| `courses/` | Reusable course, session, and assignment definitions |
| `cohorts/` | Real delivery schedules and enrollment lists |
| `students/students.yml` | Canonical minimal student registry |
| `tracking/` | Submission, attendance, and assessment facts |
| `scripts/` | Validation, safe assignment checking, progress, and reports |
| `templates/` | Documented examples for every record type |
| `reports/` | Derived private report artifacts |
| `tasks/` | Preserved legacy learner notes; not canonical progress |
| `.github/` | Issue forms, review ownership, and least-privilege workflows |

## Key documentation

- [Architecture and data ownership](docs/architecture.md)
- [Audit and migration report](docs/audit-and-migration.md)
- [Automation](docs/automation.md)
- [Security](docs/security.md)
- [Add a course](docs/adding-a-course.md)
- [Create a cohort](docs/creating-a-cohort.md)
- [Training resource catalog](docs/resource-catalog.md)
- [Testing](docs/testing.md)

The original `markdown.md`, logo, and legacy `tasks/` files are preserved. They are learning material and migration evidence, not validated completion records.
