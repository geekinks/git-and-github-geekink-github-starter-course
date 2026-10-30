# Automation

## Validate training data

Runs on relevant pull requests, pushes to `main`, and manual dispatch. It validates schemas, uniqueness, references, paths, course composition, and the full unit-test suite.

## Validate assignment submissions

Runs only for pull requests that change `tracking/submissions/`. It checks out the untrusted pull request without persisted credentials, validates only changed YAML records, checks configured files/headings/URLs, and never executes student code. It does not comment, approve, or write to the repository.

## Generate cohort reports

Runs weekly, manually, and after canonical data changes. It validates first, calculates derived reports, and uploads a 30-day private Actions artifact. It does not push commits or publish Pages.

All workflows declare `contents: read`, use timeouts and concurrency, and pin GitHub-maintained actions to reviewed commits. There are no required secrets. Local workflow testing with `act` can catch container-level errors, but GitHub event payloads, permissions, protected branches, issue forms, and Pages behavior still require a GitHub test repository.
