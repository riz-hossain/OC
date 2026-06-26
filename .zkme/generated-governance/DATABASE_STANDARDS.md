# Database Standards

No database schema or migration surface was detected; keep DB guidance as a review gate only.

## Schema Rules

- Database changes require ordered migrations, rollback or forward-fix notes, tests, consumer updates, and documentation.
- Preserve tenant, scope, authorization, and retention filters.
- Add indexes for new persistent query patterns when data size warrants it.
- Keep transactions short and avoid network calls inside transactions unless unavoidable and documented.

## Query Rules

- Identify expected row counts.
- Test empty, duplicate, malformed, and boundary cases.
- Avoid loading unbounded data into memory.

## ZKME Database Evidence

- architectureStandards: `SYSTEM_OVERVIEW.md`, `L2_CONTEXT.md`, `ZKME_REPO_PROFILE.json`, `static/files.json`
- developmentStandards: `ZKME_CHANGE_IMPACT.json`, `ZKME_CONTRACTS_INVARIANTS.json`, `static/hot_files.json`
- uiUxStandards: `static/locator_policy.v1.json`, `static/layout_tokens.json`, `static/ui_event_bindings.v1.json`, `static/frontend_calls.json`
- qaStandards: `static/negative_test_matrix.v1.json`, `static/assertion_anchors.v1.json`, `static/data_matrix.v1.json`
- securityStandards: `static/auth_contract.v1.json`, `KNOWN_HAZARDS.md`, `static/hazards.json`
- performanceStandards: `static/runtime_constraints.v1.json`, `static/hot_files.json`, `ZKME_CHANGE_IMPACT.json`
- databaseStandards: `static/db_migrations_intelligence.v1.json`, `DATA_TOUCH_MAP.json`
- i18nStandards: `static/files.json`
- reportingStandard: `00_START_HERE.md`
