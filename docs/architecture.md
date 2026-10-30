# Architecture and data model

The repository is the datastore. YAML holds auditable facts, JSON Schema defines shape, Python performs cross-record validation and derives progress, and GitHub provides identity, review, history, and automation.

## Ownership and stable IDs

- A course defines reusable learning content.
- A cohort references one course and supplies delivery dates.
- `students/students.yml` is the only canonical student registry.
- `enrollment.yml` joins stable student IDs to a cohort.
- Sessions and assignments belong to a course; attendance, submissions, and assessments belong to a cohort.
- Filenames are never identity. IDs use restricted characters, and the validator rejects absolute or parent-traversal paths.

Instructor-owned facts are cohort setup, enrollment, attendance, assessments, approval statuses, and completion. Students can propose registration and submission facts. `CODEOWNERS`, required reviews, and branch protection enforce that boundary on GitHub.

## Progress calculation

For each enrolled student, the newest submission for each required assignment is authoritative. `approved` and `completed` count as approved. `present` and `late` count toward attendance; `absent` and `excused` remain auditable but do not count. A final assessment counts only when its result is `passed` and its percentage meets the course threshold.

Progress is the equal-weight mean of assignment approval, attendance requirement, and—when required—final assessment. Completion requires all three configured gates. Commit count is never used.

Reports are derived and idempotent: rerunning against unchanged data writes the same content. Concurrent workflows cannot overwrite canonical data because reporting has read-only permissions and one non-cancelling concurrency group.

## Growth path

New programmes add configuration and content, not workflows. If repository volume or privacy requirements outgrow Git, the schemas and stable IDs form an export boundary for an authenticated service and database. That migration is not justified yet.
