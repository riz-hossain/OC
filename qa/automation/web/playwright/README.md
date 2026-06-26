# Playwright Web E2E

Use this folder for local web E2E tests generated or maintained after AI-authored feature changes.

## Rules

- Prefer `getByRole`, `getByLabel`, `getByTestId`, accessible names, and stable IDs before CSS or XPath.
- Use web-first assertions.
- Keep setup, login, and teardown reusable.
- Store generated tests in the repo's existing E2E location if one exists; otherwise use this folder as the ZKME-managed location.
- When a Playwright test mirrors a ZeuZ flow, record the ZeuZ candidate under `qa/automation/zeuz/`.
- When a Playwright test is generated from `qa/automation/local-runner/test-cases/`, keep the portable testcase as the source of truth and include its id/path in the spec comments or metadata.
- Prefer direct execution through the local runner's Playwright adapter for generated cross-surface flows; export a standalone Playwright spec when developers need normal Playwright CLI/debug ergonomics.

## UI Artifacts To Check

- `static/ui/ui_model.v1.json`
- `static/ui_surface_index.json`
- `static/locator_policy.v1.json`
- `static/ui_event_bindings.v1.json`
- `static/frontend_calls.json`
