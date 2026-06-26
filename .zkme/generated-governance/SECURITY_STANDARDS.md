# Security Standards

Security standards always apply.

## Baseline

- Do not add authentication bypasses, authorization bypasses, credential exposure, exploit flows, unsafe scanning, or secret logging.
- Validate inputs at trust boundaries.
- Encode outputs that cross trust boundaries.
- Preserve distinguishable error categories without leaking internals.
- Keep audit behavior intact for sensitive decisions.

## Sensitive Changes

Stop and plan before changing authentication, authorization, credential storage, encryption, token handling, billing, deletion, admin flows, audit behavior, or policy enforcement.

## Required Negative Tests

- unauthenticated access
- wrong-role access
- tenant or scope isolation
- expired or malformed token behavior
- invalid input and boundary values
- denied, partial, and dependency-failure states

## ZKME Security Evidence

- architectureStandards: `SYSTEM_OVERVIEW.md`, `L2_CONTEXT.md`, `ZKME_REPO_PROFILE.json`, `static/files.json`
- developmentStandards: `ZKME_CHANGE_IMPACT.json`, `ZKME_CONTRACTS_INVARIANTS.json`, `static/hot_files.json`
- uiUxStandards: `static/locator_policy.v1.json`, `static/layout_tokens.json`, `static/ui_event_bindings.v1.json`, `static/frontend_calls.json`
- qaStandards: `static/negative_test_matrix.v1.json`, `static/assertion_anchors.v1.json`, `static/data_matrix.v1.json`
- securityStandards: `static/auth_contract.v1.json`, `KNOWN_HAZARDS.md`, `static/hazards.json`
- performanceStandards: `static/runtime_constraints.v1.json`, `static/hot_files.json`, `ZKME_CHANGE_IMPACT.json`
- databaseStandards: `static/db_migrations_intelligence.v1.json`, `DATA_TOUCH_MAP.json`
- i18nStandards: `static/files.json`
- reportingStandard: `00_START_HERE.md`
