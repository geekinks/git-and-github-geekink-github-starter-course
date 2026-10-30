# Repository audit and migration

## What existed

The audit inspected every tracked file in the target repository: `README.md`, `markdown.md`, `logo.png`, `.github/.keep`, `.github/workflows/classroom.yml`, and six files in `tasks/`. Git history and the origin remote were also checked.

- The README contained useful beginner explanations and a 13-person public roster, but mixed content, enrollment, and progress concerns.
- `markdown.md` is a small worked Markdown example and remains unchanged.
- `tasks/Aminullah.md` and `tasks/EXCLUSIVE999` contain informal learner reflections. They do not prove assignment approval.
- `tasks/Mahdikabir-hub.md` and `tasks/Sumybooks2025-code.md` are empty. `tasks/umar faruoq` only says “Add username”.
- `tasks/AdamsGeeky.md` is named for one GitHub user but its content names Sumayya Tijjani Muhammad. It cannot safely be assigned to either student.
- The Classroom workflow ran a Python grader despite there being no Python exercise or tests. It used moving action tags, triggered on every push, and requested `checks: write`. It was replaced rather than retained.

## Migration decisions

The 13 README roster entries were migrated into one canonical minimal registry with stable IDs. A task file supplemented the display name only where its filename and content were consistent. No cohort enrollment, attendance, submission status, score, approval, or completion was invented. Legacy task files remain untouched for instructor review.

The malformed `github.com/geekynafisa` roster link was normalized to the username `geekynafisa`; this is a syntax correction, not online account verification. Instructors must validate account ownership during registration.

No real cohort was created because the old repository has no authoritative course dates, schedule, cohort identifier, enrollment approval, or deadlines.

## Referenced training resources

All requested sibling directories were present and inspected. Their README, lesson-step, workflow, source, and exercise-authoring structures informed the six-session mapping. They are separate repositories and are not silently copied into this one. See `resource-catalog.md`.
