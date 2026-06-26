# ZKME Testcase Packages

This folder is the canonical source of truth for generated and AI-maintained automation.

ZKME seeds package candidates from the deterministic lead-QA model in `qa/feature-architecture-map.json`, `qa/test-oracles.json`, `qa/risk-matrix.json`, `qa/test-data-matrix.json`, and `qa/traceability-matrix.json`. The manual cases under `qa/manual/test-cases/lead-qa-generated/` define the expected architecture depth for each package.

Each testcase should live as one package:

```text
qa/automation/testcases/<case-id>/
  manifest.json
  logical-testcase.json
  zeuz-bindings.json
  implementations/
    portable/testcase.json
    playwright/*.spec.ts
    zeuz-actions/actions.json
  fixtures/
  reports/
```

## Rule

Do not maintain separate Playwright and ZeuZ testcases. Maintain one testcase package, with multiple implementations bound to the same testcase ID and step keys.

Use `stepKey` as the stable automation identity. Use `stepName` as the ZeuZ-facing binding, and keep every ZeuZ `stepName` unique inside the testcase because ZeuZ uses the name as part of step identity. Numeric ZeuZ step IDs belong in `zeuz-bindings.json` after server import; do not make runnable code depend on those numbers.

ZeuZ should import the package as a versioned testcase asset:

- logical testcase for visual review and metadata
- ZeuZ action rows for no-code/low-code execution
- Playwright/Appium/API/DB code assets when code is the better execution surface
- one report identity for every runner

The generated compatibility files under `qa/automation/local-runner/test-cases/`, `qa/automation/web/playwright/generated/`, and `qa/automation/zeuz/test-cases/` are derived views kept for existing tooling.

Before completing a feature change, run `python qa/automation/validate_test_design_quality.py --json` and keep the package aligned with the lead-QA case it implements.
