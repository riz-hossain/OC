# End-To-End Tests

E2E tests should cover critical user workflows and high-risk integrations. Do not create broad brittle E2E coverage for logic that is better tested with unit, API, or integration tests.

## Rules

- Prefer Playwright for web UI unless this repo already has a stronger E2E standard.
- Keep each E2E test tied to one workflow.
- Use stable locators and deterministic data.
- Avoid raw sleeps.
- Capture screenshots/traces only where useful for debugging.
- Add a manual test candidate when automation confidence is low.
