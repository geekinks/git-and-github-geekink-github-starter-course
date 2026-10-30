# Adding a course

1. Copy `templates/course.yml` to `courses/<course-id>/course.yml`.
2. Add session files from `templates/session.yml` and assignment files from `templates/assignment.yml`.
3. Use stable lowercase IDs. Reference every session and assignment from the course file.
4. Set completion requirements explicitly; do not rely on commit counts.
5. Add human-readable course guidance and lesson material without embedding automation logic.
6. Run validation and tests.

```bash
python scripts/validate_data.py
python -m unittest discover -s tests -v
```

The existing workflows discover the new configuration automatically. No workflow copy is needed.
