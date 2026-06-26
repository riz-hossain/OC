# ZeuZ-Compatible Test Exports

This folder is for ZeuZ-compatible test-case candidates generated after AI-authored feature work.

Phase 1 goal: keep ZeuZ compatibility baked into every repo without requiring ZeuZ Server for local work.

## Layout

- `test-cases/`: generated or draft `tc.json` candidates
- `global-steps/`: reusable action row groups
- `local-run/`: local run candidates for ZeuZ Node
- `zeuz-export-manifest.json`: source/evidence map for exports

For local execution without ZeuZ Server, use `qa/automation/local-runner/`. Store ZeuZ-compatible local result envelopes under `qa/automation/reports/zeuz-compatible/`.

If a full ZeuZ Node runtime is needed, use `qa/automation/vendor/zeuz-python-node/fetch_zeuz_node.py`. It can copy a local checkout or download the official open-source dev zip.

## Rules

- Read `.zkme/kme_output/AUTOMATION_SOLUTIONZ_ZEUZ_KIT.md` when present.
- Read `.zkme/kme_output/static/automation_solutionz_zeuz_kit.v1.json` when present.
- Read `.zkme/kme_output/static/zeuz_function_catalog.v1.json` when present.
- Use known ZeuZ action names and valid row sub-fields.
- Keep `stepKey` stable across logical, portable, Playwright, ZeuZ action, and report views.
- Keep ZeuZ-facing `stepName` values unique inside each testcase; ZeuZ currently treats step names as identity bindings.
- Use `%|variable_name|%` only when the variable is created or supplied.
- Prefer stable locators from ZKME locator policy.
- Reuse global steps when repeated action groups appear.
- Keep ZeuZ Server sync as a draft/review step, not a silent overwrite of reviewed test cases.
- If a local Playwright E2E test mirrors this flow, link it from the export manifest.
- If a portable local testcase runs this flow, link it from the export manifest and preserve the `zeuzExecutionLog` report projection under `qa/automation/reports/zeuz-compatible/`.
