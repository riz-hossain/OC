# Manual Test Cases

Every AI-authored feature change must add or update a manual acceptance test case here unless the change is documentation-only.

Use `FEATURE_TEST_CASE.template.md` as the shape. A manual test case is required even when unit or E2E automation is added, because it gives ZeuZ, QA, product, and future AI agents a readable source of truth.

ZKME may generate deterministic lead-QA cases under `lead-qa-generated/`. Treat those as the minimum quality floor. A replacement or edited case must preserve the same architecture depth: UI/mobile/desktop, API, DB, auth/role, audit/report/log, negative, boundary, fixture, traceability, cleanup, and artifact validation whenever applicable.

## Required Fields

- feature or workflow
- source evidence
- preconditions
- test data
- steps
- expected results
- negative cases
- automation candidate
- ZeuZ export candidate
- accessibility, security, performance, DB, and i18n notes when applicable
