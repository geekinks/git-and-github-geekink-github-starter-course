# Instructor guide

## 1. Set up the repository

Install Python dependencies, run validation and tests, create a `training-instructors` team or update `.github/CODEOWNERS`, then configure the protected `main` branch as described in `security.md`.

```bash
python -m pip install -r requirements.txt
python scripts/validate_data.py
python -m unittest discover -s tests -v
```

## 2. Add courses and cohorts

Follow `adding-a-course.md` for a reusable course. Follow `creating-a-cohort.md` for each delivery. Session dates and assignment due offsets are separate so the same course can run again.

## 3. Register and enroll a student

Review the registration issue, open the claimed GitHub profile, and confirm the username with the learner. Assign the next stable ID, add one record to `students/students.yml`, add only the ID to the cohort enrollment list, and merge through review. Close the issue with the assigned ID and course instructions.

## 4. Assign materials

Share the course README, session configuration, and applicable linked GitHub Skills exercise. Cohort dates determine when work happens; assignments define submission requirements.

## 5. Record attendance

Copy `templates/attendance.yml` after each session, fill every enrolled student explicitly, and commit it to `tracking/attendance/`. Do not infer attendance from commits. Use factual, non-sensitive notes.

## 6. Review submissions

Use the `submission` and `instructor-review` issue labels or the report queue. Inspect workflow output, then assess the learning objectives yourself. Record actionable feedback. Change the canonical submission status to `changes_requested` or `approved` through an instructor-reviewed pull request; never equate a green check with approval.

## 7. Handle failed checks

Open the failed job, read the exact path and rule, and ask the learner to correct the record or artifact. Do not disable a check to force approval. If a rule is wrong, fix the course assignment and add a regression test.

## 8. Assess and complete

Copy `templates/assessment.yml` into `tracking/assessments/`, score against the published rubric, and record concise feedback. Generate reports:

```bash
python scripts/generate_report.py --cohort github-starter-2027-01
```

Review completion gates and correct source records rather than editing the report. The reports workflow also provides a private Actions artifact.

After verifying the final report, copy `templates/completion.yml` into `tracking/completions/` to create the instructor-approved course completion record.

## 9. Archive and start again

Resolve outstanding reviews, generate the final report, change the cohort status to `completed`, and later to `archived`. Keep records immutable except for documented corrections. Create the next cohort from the same course; do not copy workflows.
