# AI Instructions (ZKME)
This repo was scanned by **ZKME (ZeuZ Knowledge Map Engine)**.
## Non-negotiable rules
1. **SNAPSHOT/STATIC is authoritative.** Do not contradict it.
2. **Use the artifacts below before proposing changes.** If a relevant artifact is missing, say **UNKNOWN**.
3. **For every file you change (or recommend changing), list the artifacts you used.**
4. If hard facts conflict with soft guidance, **hard facts win**.
5. If generated, read `ZKME_GOVERNANCE_PACK.md` before coding and follow its hard-stop, planning, QA, security, performance, DB, i18n, and reporting rules.

## Governance Rules
Use these rules for every meaningful code task:

1. Stop before broad, ambiguous, strategic, security-sensitive, data-model, API, event, migration, background-job, credential, billing, deletion, admin, or audit changes.
2. Use numbered planning for substantial work and re-check architecture, UI/UX, QA, security, performance, DB, and i18n after each 25 percent on large tasks.
3. Preserve existing architecture and contracts unless the user explicitly approved a contract change.
4. For UI/UX work, read `ZKME_GOVERNANCE_PACK.md` / `UI_UX_STANDARDS.md` if present, then inspect `static/ui/ui_model.v1.json`, `static/layout_tokens.json`, `static/locator_policy.v1.json`, and `static/ui_event_bindings.v1.json` when available. Reuse existing components, tokens, layout patterns, and locator policy before creating new UI.
5. Choose the smallest QA gate that covers risk, then broaden when shared contracts move.
6. Never weaken auth/authz, secret handling, validation, audit, or policy behavior without explicit approval and negative tests.
7. Bound lists, searches, parsing, retries, concurrency, background work, and exports.
8. Treat DB schema or query changes as high-risk: require migrations, tests, rollback/forward-fix notes, indexes where needed, and consumer updates.
9. Keep user-facing strings localization-ready; do not force a broad i18n retrofit unless requested.
10. Final reports must include ZKME artifacts consulted, surfaces found via ZKME, estimated time saved, mismatches, tests run/not run, and security/performance/DB/i18n notes.

## How to work efficiently (load order)
1) `00_START_HERE.md` — navigation guide — read this FIRST
2) `ZKME_GOVERNANCE_PACK.md` — AI governance rules for this scanned repo
3) `SYSTEM_OVERVIEW.md` — repo scale, tech stack, interfaces
4) `KNOWN_HAZARDS.md` — what not to break
5) Task-specific files (see below)
6) `static/` JSONs for precise, provable answers
7) `GIT_LEARNING/` for risk/intent heuristics (guidance only, not facts)

## Task-Specific Navigation
> **TIP**: For detailed workflows and example prompts, read `ZKME_DEV_GUIDE.md` (development tasks) or `ZEUZ_TEST_GUIDE.md` (ZeuZ test generation).

### For Bug Analysis / Fix Planning
1. `KNOWN_HAZARDS.md` — sensitive areas that could break
2. `static/hot_files.json` — most important files ranked with reasons
3. `static/frontend_calls.json` — frontend-to-backend call mapping
4. `static/routes_detected.json` — API surface (routes)
5. `static/import_edges.json` — blast radius (what breaks if X changes)
6. `ZKME_CHANGE_IMPACT.json` — 2-hop change impact graph
7. `ZKME_PATHS.json` — golden paths (interface -> call chain -> DB)
8. `KME_CONFIDENCE_REPORT.json` — confidence scores — which facts are HIGH vs LOW

**Power features for bug analysis:**
- **Blast radius**: Cross-reference `ZKME_CHANGE_IMPACT.json` with `static/import_edges.json` to find every file affected by your fix.
- **Confidence check**: Read `KME_CONFIDENCE_REPORT.json` to know which facts about the codebase are HIGH confidence vs LOW (avoid relying on LOW-confidence data).

### For Requirement / Feature Planning
1. `SYSTEM_OVERVIEW.md` — repo scale, languages, interfaces
2. `L2_CONTEXT.md` — entry points, data models, call chains, config
3. `INTERFACE_CATALOG.json` — all API endpoints
4. `ZKME_FEATURE_REGISTRY.json` — existing features with core files
5. `ZKME_CONTRACTS_INVARIANTS.json` — rules that must be preserved
6. `KME_AGGREGATION_CANDIDATES.json` — machine-extracted interface contracts and aggregation points
7. `KME_RECOMMENDED_CONTRACTS.json` — recommended contracts for new features

**Power features for feature planning:**
- **Interface contracts**: `KME_AGGREGATION_CANDIDATES.json` contains machine-extracted contracts from the codebase — use these to understand existing boundaries before adding new ones.

### For UI/UX Design / Frontend Work
1. `ZKME_GOVERNANCE_PACK.md` — design-system-first UI rules and required UI report fields
2. `static/ui_surface_index.json` — pages, selectors, actions, and assertions
3. `static/layout_tokens.json` — layout, sizing, overflow, grid, flex, table, and responsive-risk signals
4. `static/locator_policy.v1.json` — selector priority and locator stability policy
5. `static/ui_event_bindings.v1.json` — UI-to-action/API binding coverage
6. `static/frontend_calls.json` — frontend-to-backend call mapping
7. `static/assertion_anchors.v1.json` — existing assertion anchors and test coverage hints

**UI consistency rules:**
- Reuse existing components, variants, design tokens, layout patterns, icon patterns, form patterns, table patterns, empty states, and error states first.
- Do not create parallel buttons, inputs, cards, modals, tables, badges, navigation, search, filters, or toast systems.
- Add a new component only when existing components cannot be cleanly extended and the new component follows local naming, props, styling, state, accessibility, and selector conventions.
- Cover empty, loading, error, denied, partial, success, accessibility, keyboard/focus, responsive, and i18n text-fit states.

### For Test Planning
1. `static/flow_graph.v1.json` — end-to-end user flow graph
2. `static/negative_test_matrix.v1.json` — negative test scenarios
3. `static/data_matrix.v1.json` — data combinations for parameterized tests
4. `static/assertion_anchors.v1.json` — existing test assertion locations
5. `static/auth_contract.v1.json` — authorization rules to test
6. `static/ui_event_bindings.v1.json` — UI-to-API event bindings

**Test automation policy:**
- If present, read `qa/AI_TEST_GENERATION_CONTRACT.md` before implementing feature work.
- Generate tests from ZKME/source evidence, not generic guesses.
- Create or update a manual test case under `qa/manual/test-cases/` for feature work.
- Prefer local runnable automation before requiring a server-side test manager.
- For web UI, prefer Playwright when no stronger project-local standard exists.
- For API/service behavior, use the existing repo test stack and deterministic fixtures.
- For DB, mobile, desktop, REST/API, performance, security, or cross-surface workflows, keep ZeuZ-compatible action/export candidates when requested.
- Low-confidence automation should become a manual test candidate, not brittle generated code.

### For ZeuZ Test Case Generation
**Read `ZEUZ_TEST_GUIDE.md`** for the complete workflow, tc.json format, and row patterns.

ZeuZ is a first-party compatibility target. Local tests should still be useful without ZeuZ Server, but generated test cases should preserve a path to ZeuZ Node local runs and future ZeuZ Server draft sync when requested.

**IMPORTANT — follow this order:**

1. **Learn from this project's tests**: Read `ZEUZ_EXAMPLE_TESTS/INDEX.json`, then open 2-3 example tc.json files similar to what you need. Study how steps are named, how actions use row patterns, and how variables flow between steps. Your output must match these conventions.
2. **Reuse global steps**: Read `ZEUZ_GLOBAL_STEPS/INDEX.json`. If a global step exists for what you need (login, navigate, fill form, etc.), use it directly — copy the actions array and replace placeholder selectors with real values from `static/ui_surface_index.json`.
3. **Get selectors + endpoints**: Read `static/ui_surface_index.json` (pages, selectors), `static/api_surface_index.json` (REST/GraphQL), `static/db_surface_index.json` (DB).
4. **Generate**: Compose from global steps where possible. For new steps, follow the exact patterns from the examples. Never invent selectors or URLs — use UNKNOWN if not found.

**Example prompt for AI:**
```
Read kme_output/ZEUZ_TEST_GUIDE.md.
Study 2-3 similar examples from kme_output/ZEUZ_EXAMPLE_TESTS/.
Check kme_output/ZEUZ_GLOBAL_STEPS/INDEX.json for reusable steps.
Read the static indexes for selectors and endpoints.
Generate a ZeuZ tc.json test for: [describe your feature]
```

**CLI quick start:**
```bash
zkme test . "Login flow" --objective "Verify user can log in" --model gpt-4o
```

### For Task / Refactoring
1. `ZKME_CHANGE_IMPACT.json` — blast radius for files you plan to change
2. `ZKME_CONTRACTS_INVARIANTS.json` — invariants that must be preserved
3. `static/hierarchy.json` — class inheritance chains
4. `static/call_graph.json` — function call edges
5. `ZKME_PATCH_PLANNING_PACK.md` — pre-change checklist

## Cross-Reference Hints
These artifact pairs are most powerful when read together:

- `ZKME_CHANGE_IMPACT.json` + `static/import_edges.json`: impact graph + import edges = complete blast radius for any change
- `static/flow_graph.v1.json` + `static/ui_event_bindings.v1.json`: user flow graph + UI event bindings = complete interaction map
- `static/routes_detected.json` + `static/frontend_calls.json`: backend routes + frontend calls = full API contract
- `KME_CONFIDENCE_REPORT.json` + `SYSTEM_OVERVIEW.md`: confidence guide tells you which parts of the overview are most reliable

## Quick Reference
| If you need... | Read this file |
|----------------|---------------|
| Repo overview (start here) | `SYSTEM_OVERVIEW.md` |
| API endpoints | `INTERFACE_CATALOG.json` |
| Data models / schemas | `static/schemas.json` |
| What breaks if I change X | `ZKME_CHANGE_IMPACT.json` |
| Dangerous areas | `KNOWN_HAZARDS.md` |
| Auth / permission rules | `static/auth_contract.v1.json` |
| Test coverage gaps | `static/assertion_anchors.v1.json` |
| Frontend-to-Backend mapping | `static/frontend_calls.json` |
| Git history hot spots | `GIT_LEARNING/10_HOT_FILES.csv` |
| Full working context | `L2_CONTEXT.md` |
| Fact confidence scores | `KME_CONFIDENCE_REPORT.json` |
| Interface contracts | `KME_AGGREGATION_CANDIDATES.json` |
| ZeuZ test generation | `ZEUZ_TEST_GUIDE.md` |
| ZeuZ function/action capability catalog | `ZEUZ_FUNCTION_CATALOG.md` |
| Machine-readable ZeuZ function/action catalog | `static/zeuz_function_catalog.v1.json` |
| Automation Solutionz / ZeuZ QA kit | `AUTOMATION_SOLUTIONZ_ZEUZ_KIT.md` |
| Machine-readable Automation Solutionz / ZeuZ QA kit | `static/automation_solutionz_zeuz_kit.v1.json` |
| Real test examples | `ZEUZ_EXAMPLE_TESTS/INDEX.json` |
| Reusable test steps | `ZEUZ_GLOBAL_STEPS/INDEX.json` |
| Development workflows | `ZKME_DEV_GUIDE.md` |
| AI governance pack | `ZKME_GOVERNANCE_PACK.md` |
| Governance manifest and citations | `ZKME_GOVERNANCE_MANIFEST.json` |
| Governance validation checks | `ZKME_GOVERNANCE_VALIDATION.json` |
| UI layout/design token signals | `static/layout_tokens.json` |
| UI locator priority policy | `static/locator_policy.v1.json` |
| UI action/API bindings | `static/ui_event_bindings.v1.json` |
| Available UI selectors | `static/ui_surface_index.json` |
| API endpoints for testing | `static/api_surface_index.json` |

## End-user prompt (keep it short)
Copy/paste this as your request:
> **Make the safest change to <YOUR_GOAL>. Follow ZKME rules and cite artifacts used for each edited file.**

## Hard facts (authoritative)
Deterministic artifacts produced by ZKME. Treat as truth.
- `static/active_surface_index.json`
- `static/api_surface_index.json`
- `static/assertion_anchors.v1.json`
- `static/ast_errors.json`
- `static/auth_contract.v1.json`
- `static/automation_solutionz_zeuz_kit.v1.json`
- `static/call_graph.json`
- `static/config_keys.json`
- `static/data_matrix.v1.json`
- `static/data_touches.json`
- `static/db_migrations_intelligence.v1.json`
- `static/db_surface_index.json`
- `static/decorators.json`
- `static/desktop_surface.v1.json`
- `static/evidence_index.json`
- `static/features.json`
- `static/files.json`
- `static/flow_graph.v1.json`
- `static/frontend_calls.json`
- `static/graphql_index.json`
- `static/guard_clauses.v1.json`
- `static/hazards.json`
- `static/hierarchy.json`
- `static/hot_files.json`
- `static/imports.json`
- `static/import_edges.json`
- `static/interfaces.json`
- `static/layout_tokens.json`
- `static/legacy_surface_index.json`
- `static/locator_policy.v1.json`
- `static/negative_test_matrix.v1.json`
- `static/openapi_surface.v1.json`
- `static/proxy_rules.json`
- `static/ranks.json`
- `static/realtime_surface.v1.json`
- `static/repo_root_signature.json`
- `static/repo_signals.json`
- `static/routes_detected.json`
- `static/route_contracts.v1.json`
- `static/rule_engine_detection.json`
- `static/runtime_constraints.v1.json`
- `static/schemas.json`
- `static/search_backend_detected.json`
- `static/side_effects_map.v1.json`
- `static/state_enum_index.v1.json`
- `static/symbols.json`
- `static/test_data_contract.v1.json`
- `static/types.json`
- `static/ui_event_bindings.v1.json`
- `static/ui_surface_index.json`
- `static/websocket_surface_index.json`
- `static/zeuz_function_catalog.v1.json`
- `ZKME_GOVERNANCE_PACK.md`
- `ZKME_GOVERNANCE_MANIFEST.json`
- `ZKME_GOVERNANCE_VALIDATION.json`
- `AUTOMATION_SOLUTIONZ_ZEUZ_KIT.md`
- `ZEUZ_FUNCTION_CATALOG.md`

## Soft guidance (git history)
Heuristic signals from Git history. Use for **risk/intent** only. Do not treat as facts.
- `GIT_LEARNING/00_SNAPSHOT_GIT_HISTORY.json`
- `GIT_LEARNING/10_HOT_FILES.csv`
- `GIT_LEARNING/20_TOP_AUTHORS.csv`
- `GIT_LEARNING/30_FILE_COUPLING.csv`
- `GIT_LEARNING/40_LLM_PROMPT.md`
- `GIT_LEARNING/90_VALIDATION.json`

## Derived (LLM enrichment outputs, if present)
Optional analysis-only outputs. Helpful context, but not authoritative over hard facts.
- (none found)
