# Performance Standards

Performance standards always apply.

## Required Review

- Define expected data size, latency budget, memory budget, concurrency assumptions, timeout behavior, and degradation behavior for performance-sensitive changes.
- Paginate or bound unbounded lists and searches.
- Avoid N+1 data access.
- Stream or chunk large exports.
- Avoid broad locks around slow work.
- Keep cancellation and timeout behavior visible.

## Frontend And Mobile

- Avoid rendering unbounded lists without pagination or virtualization.
- Keep loading dimensions stable.
- Avoid expensive filtering on every keystroke for large data.
- For mobile, avoid blocking the UI thread and consider startup, low memory, offline, and poor-network behavior.

## ZKME Performance Evidence

- architectureStandards: `SYSTEM_OVERVIEW.md`, `L2_CONTEXT.md`, `ZKME_REPO_PROFILE.json`, `static/files.json`
- developmentStandards: `ZKME_CHANGE_IMPACT.json`, `ZKME_CONTRACTS_INVARIANTS.json`, `static/hot_files.json`
- uiUxStandards: `static/locator_policy.v1.json`, `static/layout_tokens.json`, `static/ui_event_bindings.v1.json`, `static/frontend_calls.json`
- qaStandards: `static/negative_test_matrix.v1.json`, `static/assertion_anchors.v1.json`, `static/data_matrix.v1.json`
- securityStandards: `static/auth_contract.v1.json`, `KNOWN_HAZARDS.md`, `static/hazards.json`
- performanceStandards: `static/runtime_constraints.v1.json`, `static/hot_files.json`, `ZKME_CHANGE_IMPACT.json`
- databaseStandards: `static/db_migrations_intelligence.v1.json`, `DATA_TOUCH_MAP.json`
- i18nStandards: `static/files.json`
- reportingStandard: `00_START_HERE.md`
