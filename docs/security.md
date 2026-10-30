# Security and repository settings

Student content is untrusted. Workflows use `pull_request`, never `pull_request_target`; persist no checkout credentials in submission validation; execute no submitted programs; expose no secrets; and grant read-only contents access. Path validation rejects absolute paths and traversal.

## Required GitHub settings

1. Replace the placeholder team in `.github/CODEOWNERS` or create `@geekinks/training-instructors`.
2. Protect `main`: require pull requests, at least one Code Owner approval, conversation resolution, and the training-data validation check.
3. Prevent force pushes and branch deletion on `main`.
4. Limit Actions to trusted actions and reusable workflows; keep default workflow permissions read-only.
5. Enable secret scanning and dependency alerts when the plan supports them.
6. Restrict repository visibility if student identities or results must not be public.

GitHub Pages is not an access-control system for private grades or notes, so this implementation does not deploy the dashboard. Reports remain local or in access-controlled Actions artifacts. Issue labels and CODEOWNERS help workflow but are not authorization by themselves; branch protection supplies enforcement.

No secrets are required. If a future notification integration needs one, use an organization/repository secret with the narrowest scope and never expose it to fork pull-request jobs.
