# Tracking records

- `submissions/` contains student submission metadata. Students may create records with `submitted` status; passing automation does not approve work.
- `attendance/` contains explicit instructor-recorded attendance. Activity and commits never imply attendance.
- `assessments/` contains instructor-only scores and decisions.
- `completions/` contains instructor-approved completion snapshots that reference a derived report.

Directories contain no fabricated production records. Copy the relevant template when real data exists. Protect instructor-owned paths with `CODEOWNERS` and branch protection.
