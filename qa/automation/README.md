# QA Automation

Read `../AI_TEST_GENERATION_CONTRACT.md` before adding or changing feature code.

## Detected Commands

- No build, test, lint, or typecheck command was detected. Use UNKNOWN instead of inventing one.

## Suites

- Unit: business logic, validators, parsing, permissions helpers, state transitions, and utilities.
- Integration: service, DB, worker, queue, or cross-module behavior.
- API: contract and service behavior.
- Web: Playwright critical user flows when UI surfaces are affected.
- E2E: end-to-end workflow tests where unit/API/integration coverage is not enough.
- Mobile: use only when mobile surfaces are detected.
- Desktop: use only when desktop surfaces are detected.
- DB: query, migration, and data-integrity checks.
- ZeuZ: cross-surface action candidates for Web/API/DB/Mobile/Desktop/Performance/Security flows.
- Performance: smoke checks for data-size, latency, memory, and concurrency risk.
- Security: auth/authz, validation, secret redaction, and policy-denial checks.

Reports should include command, environment, start/end time, pass/fail/skip counts, failures, and artifacts.

## Lead-QA Design Gate

ZKME creates deterministic test-design artifacts in `../feature-architecture-map.json`, `../workflow-map.json`, `../test-oracles.json`, `../risk-matrix.json`, `../test-data-matrix.json`, `../traceability-matrix.json`, and `../test-design-quality.json`. These files tell AI agents which UI/mobile/desktop, API, DB, auth, audit/report/log, negative, boundary, cleanup, fixture, traceability, and artifact evidence must exist for each detected feature.

Validate that generated or edited manual cases preserve this depth:

```bash
python qa/automation/validate_test_design_quality.py --json
```

## Contract Gate

Use the generated verifier to make the QA rules executable:

```bash
python qa/automation/verify_zkme_qa_contract.py --changed-file path/to/changed/file
```

For CI:

```bash
git diff --name-only origin/main...HEAD > .zkme/changed-files.txt
python qa/automation/verify_zkme_qa_contract.py --changed-files-from .zkme/changed-files.txt
```

This gate fails when touched surfaces are missing the required manual, unit, API, DB, web, mobile, desktop, portable, or ZeuZ-compatible evidence.
