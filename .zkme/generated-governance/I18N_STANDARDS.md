# I18N Standards

i18n readiness always applies.

## Rules

- If the project has localization, use translation keys for user-facing strings.
- If the project has no localization layer, do not force a broad retrofit during unrelated work.
- Centralize new user-facing copy where practical.
- Avoid duplicate ad hoc messages.
- Keep labels stable and translation-ready.
- Test or reason about longer translated strings and RTL only where the project promises RTL.

## Applies To

- UI labels
- validation messages
- errors
- reports
- emails
- notifications
- help text
- generated QA instructions

## ZKME I18N Evidence

- architectureStandards: `SYSTEM_OVERVIEW.md`, `L2_CONTEXT.md`, `ZKME_REPO_PROFILE.json`, `static/files.json`
- developmentStandards: `ZKME_CHANGE_IMPACT.json`, `ZKME_CONTRACTS_INVARIANTS.json`, `static/hot_files.json`
- uiUxStandards: `static/locator_policy.v1.json`, `static/layout_tokens.json`, `static/ui_event_bindings.v1.json`, `static/frontend_calls.json`
- qaStandards: `static/negative_test_matrix.v1.json`, `static/assertion_anchors.v1.json`, `static/data_matrix.v1.json`
- securityStandards: `static/auth_contract.v1.json`, `KNOWN_HAZARDS.md`, `static/hazards.json`
- performanceStandards: `static/runtime_constraints.v1.json`, `static/hot_files.json`, `ZKME_CHANGE_IMPACT.json`
- databaseStandards: `static/db_migrations_intelligence.v1.json`, `DATA_TOUCH_MAP.json`
- i18nStandards: `static/files.json`
- reportingStandard: `00_START_HERE.md`
