# QA Automation Standards

## QA Status

qa/ structure not detected

## Detected Commands

- No build, test, lint, or typecheck command was detected. Use UNKNOWN instead of inventing one.

## Test Priority

1. Unit and parser/business-logic tests.
2. API and service contract tests.
3. Integration tests with deterministic fixtures.
4. Web critical E2E tests when UI flows are affected.
5. Mobile E2E only when mobile surfaces are detected.
6. Cross-surface ZeuZ-compatible action flows for web/API/DB/mobile scenarios when the workflow genuinely spans those surfaces.
7. Manual exploratory checks for visual polish, accessibility, deployment, and unusual paths.

## ZKME Test Automation Platform Policy

ZKME test generation must be local-first, evidence-backed, and ZeuZ-compatible.

- Read `qa/AI_TEST_GENERATION_CONTRACT.md` when present before implementing feature work.
- Read `qa/feature-architecture-map.json`, `qa/workflow-map.json`, `qa/test-oracles.json`, `qa/risk-matrix.json`, `qa/test-data-matrix.json`, `qa/traceability-matrix.json`, and `qa/test-design-quality.json` when present before designing tests.
- Generate or maintain a traceable test inventory before writing runnable automation.
- Every generated test must cite source or ZKME artifact evidence.
- Prefer local runnable tests before requiring a server-side test-management platform.
- For web UI, prefer Playwright as the default local runner because it provides auto-waiting, resilient locators, traces, and cross-browser execution.
- For API and service behavior, prefer the existing repository test framework and deterministic fixtures.
- For DB, mobile, desktop, REST/API, performance, and security cross-surface flows, reuse or export ZeuZ-compatible action concepts where practical.
- ZeuZ Server integration is optional. Generated tests should be able to run or be reviewed locally first, then sync to ZeuZ as drafts for visual editing, execution, and reporting when enabled.
- Local execution must not require ZeuZ Server. When generated tests run locally, preserve results in normal local reports and, when possible, a ZeuZ-compatible report envelope.

## Deterministic Lead-QA Test Design

ZKME creates a non-AI lead-QA model. AI agents must use it as the test-design floor, not as optional inspiration.

- `qa/feature-architecture-map.json`: feature to UI/mobile/desktop/API/DB/auth/job/integration/report evidence.
- `qa/workflow-map.json`: expected validation phases for each feature.
- `qa/test-oracles.json`: concrete UI/API/DB/auth/audit/negative expected-result targets.
- `qa/risk-matrix.json`: risk drivers and required evidence per feature.
- `qa/test-data-matrix.json`: deterministic fixture, boundary, invalid, permission, integration, cleanup, and evidence data expectations.
- `qa/traceability-matrix.json`: source evidence to manual case to automation package/report mapping.
- `qa/test-design-quality.json`: score and minimum threshold for each feature.
- `qa/manual/test-cases/lead-qa-generated/`: deep manual cases to enrich, preserve, or supersede with equal-or-better cases.
- `qa/automation/validate_test_design_quality.py`: executable quality gate. Do not finish feature work when this gate fails.

## Local Runner Defaults

| Surface | Preferred local output | ZeuZ compatibility |
|---------|------------------------|--------------------|
| Web UI | Playwright tests with project-local helpers | Export equivalent ZeuZ web/playwright or selenium action rows when requested |
| API | Existing project API test stack, pytest/requests, supertest, or Karate-style cases based on repo language | Export REST/API action rows and response variable saves |
| Database | Existing integration tests or DB fixture checks | Export DB connection/query/validation rows only with approved local test DB settings |
| Mobile | Existing mobile test stack or Appium-compatible smoke only when mobile surfaces exist | Export Appium/ZeuZ mobile action rows |
| Performance | k6-style smoke/load checks only when requested or high-risk | Export ZeuZ performance action candidates when available |
| Security | Approved local/staging ZAP-style smoke only when requested | Export ZeuZ security action candidates when available |
| Local portable runner | `qa/automation/local-runner/` portable test cases | `qa/automation/reports/zeuz-compatible/` report envelope for later ZeuZ import/sync |

## Test Intelligence Rules

- Use `static/ui/ui_model.v1.json`, `static/ui_surface_index.json`, `static/locator_policy.v1.json`, `static/frontend_calls.json`, `static/routes_detected.json`, `static/assertion_anchors.v1.json`, `static/negative_test_matrix.v1.json`, `static/data_matrix.v1.json`, `static/auth_contract.v1.json`, and database artifacts when present.
- Use the lead-QA model to force deep validation: API and DB behind UI, role/permission denial, audit/report/log evidence, cleanup, retry/idempotency, and artifacts.
- Do not invent routes, selectors, credentials, database tables, app screens, or run commands.
- Mark low-confidence automation as a manual test candidate instead of writing brittle automation.
- Prefer stable test IDs, accessible names, roles, and explicit locator contracts before CSS or XPath fallbacks.
- Keep generated tests short, named, tagged, and tied to one behavior.
- Extract repeated ZeuZ action row groups into global-step candidates.
- Preserve local report artifacts so they can later be ingested by ZeuZ Server, Allure, ReportPortal, or CI.

## Required Categories

- unit
- API contract
- integration
- parser/fixture
- golden snapshot
- web critical E2E
- mobile critical E2E when applicable
- ZeuZ-compatible cross-surface action candidate when applicable
- accessibility smoke
- performance smoke
- security smoke
- migration test when applicable
- release smoke
- manual checklist

## Test Data

- Use deterministic fixtures.
- Do not use dummy data as proof of capability.
- Keep secrets out of fixtures, reports, screenshots, and prompts.
- Keep generated ZeuZ local-run artifacts separate from hand-authored production test cases until reviewed.
- Use only approved local or staging DB/API/mobile targets for generated automation.

## ZKME QA Evidence

- architectureStandards: `SYSTEM_OVERVIEW.md`, `L2_CONTEXT.md`, `ZKME_REPO_PROFILE.json`, `static/files.json`
- developmentStandards: `ZKME_CHANGE_IMPACT.json`, `ZKME_CONTRACTS_INVARIANTS.json`, `static/hot_files.json`
- uiUxStandards: `static/locator_policy.v1.json`, `static/layout_tokens.json`, `static/ui_event_bindings.v1.json`, `static/frontend_calls.json`
- qaStandards: `static/negative_test_matrix.v1.json`, `static/assertion_anchors.v1.json`, `static/data_matrix.v1.json`
- securityStandards: `static/auth_contract.v1.json`, `KNOWN_HAZARDS.md`, `static/hazards.json`
- performanceStandards: `static/runtime_constraints.v1.json`, `static/hot_files.json`, `ZKME_CHANGE_IMPACT.json`
- databaseStandards: `static/db_migrations_intelligence.v1.json`, `DATA_TOUCH_MAP.json`
- i18nStandards: `static/files.json`
- reportingStandard: `00_START_HERE.md`
