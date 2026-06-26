# Development Standards

## Project Evidence

- Project types: library
- Languages: html, markdown
- Framework/build signals: UNKNOWN

## Commands

- No build, test, lint, or typecheck command was detected. Use UNKNOWN instead of inventing one.

## Architecture Rules

- Read `00_START_HERE.md`, `SYSTEM_OVERVIEW.md`, `KNOWN_HAZARDS.md`, `ZKME_CHANGE_IMPACT.json`, and `ZKME_CONTRACTS_INVARIANTS.json` before changing code.
- Reuse existing modules, helpers, services, patterns, and test conventions.
- Keep edits scoped to the task and affected surfaces.
- Do not create parallel implementations of services, clients, scanners, state stores, query layers, or output generators unless the existing path cannot support the requirement.
- Preserve public contracts unless approved.

## Planning Rules

- Use numbered implementation plans for substantial work.
- For large tasks, perform a 25 percent checkpoint covering architecture, UI/UX, QA, security, performance, database, i18n, and deployment risk.
- Treat examples from users as intent signals unless they explicitly say the example is the full scope.

## Surface Summary

| Surface | Count |
|---------|-------|
| API routes | 0 |
| UI surfaces | 0 |
| Mobile surfaces | 0 |
| Database tables | 0 |
| Workers | 0 |
| Queues | 0 |

## Evidence Citations

- architectureStandards: `SYSTEM_OVERVIEW.md`, `L2_CONTEXT.md`, `ZKME_REPO_PROFILE.json`, `static/files.json`
- developmentStandards: `ZKME_CHANGE_IMPACT.json`, `ZKME_CONTRACTS_INVARIANTS.json`, `static/hot_files.json`
- uiUxStandards: `static/locator_policy.v1.json`, `static/layout_tokens.json`, `static/ui_event_bindings.v1.json`, `static/frontend_calls.json`
- qaStandards: `static/negative_test_matrix.v1.json`, `static/assertion_anchors.v1.json`, `static/data_matrix.v1.json`
- securityStandards: `static/auth_contract.v1.json`, `KNOWN_HAZARDS.md`, `static/hazards.json`
- performanceStandards: `static/runtime_constraints.v1.json`, `static/hot_files.json`, `ZKME_CHANGE_IMPACT.json`
- databaseStandards: `static/db_migrations_intelligence.v1.json`, `DATA_TOUCH_MAP.json`
- i18nStandards: `static/files.json`
- reportingStandard: `00_START_HERE.md`
