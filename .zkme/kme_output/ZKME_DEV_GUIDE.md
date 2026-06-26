# ZKME Development Guide

> **For AI agents**: This guide explains how to use all the artifacts in
> `kme_output/` for development tasks — bug fixing, feature planning,
> refactoring, code review, and test planning. Each section has a
> workflow, artifact descriptions, and example prompts you can copy-paste.

---

## Overview

ZKME scanned this repository and produced artifacts organized by trust level:

| Directory / File | Trust Level | Description |
|-----------------|-------------|-------------|
| `static/` | **Authoritative** | Ground truth JSONs — files, symbols, routes, schemas, imports, call graph, hazards |
| `ZKME_CONTEXT_PACK/` | **Authoritative** | Tiered summaries: Tier1 = core truth, Tier2 = per-feature, Tier3 = reference links |
| `GIT_LEARNING/` | **Guidance only** | Git history signals (hot files, co-change coupling, author ownership) |
| `llm/` | **Derived** | Optional LLM enrichment outputs |

**Core rule**: `static/` files are facts. `GIT_LEARNING/` files are heuristics.
If you cannot prove a claim from these artifacts or the source code, write **UNKNOWN**.
For every file you change, **cite which artifacts informed the decision**.

---

## Bug Analysis / Fix Planning

### Workflow

1. **Understand the bug area** — Read `KNOWN_HAZARDS.md` to check if the bug
   touches a sensitive area (auth, payments, data integrity).
2. **Assess blast radius** — Read `ZKME_CHANGE_IMPACT.json` to see what other
   files and features are affected by changes to the buggy area.
3. **Trace the flow** — Read `ZKME_PATHS.json` to follow golden paths
   (interface → call chain → DB) through the bug area.
4. **Check hotness** — Read `static/hot_files.json` to see if the affected file
   is frequently modified (higher risk of regression).
5. **Map dependencies** — Read `static/import_edges.json` to find what modules
   import the broken file (reverse dependencies).
6. **Trace callers** — Read `static/call_graph.json` to find what functions
   call the broken function.
7. **Check API surface** — Read `static/frontend_calls.json` + `static/routes_detected.json`
   to see if the bug affects any API endpoints.

### Key Artifacts

| Artifact | What It Tells You |
|----------|-------------------|
| `KNOWN_HAZARDS.md` | Sensitive areas — auth, payments, data integrity | available |
| `ZKME_CHANGE_IMPACT.json` | 2-hop blast radius for any file you plan to change | available |
| `ZKME_PATHS.json` | Golden paths: interface → call chain → DB | available |
| `static/hot_files.json` | Most important files ranked with reasons | available |
| `static/import_edges.json` | File-level import/dependency graph | available |
| `static/call_graph.json` | Function-level call edges | available |
| `static/frontend_calls.json` | Frontend-to-backend API call mapping | available |

### Example Prompts

```
Read kme_output/ZKME_DEV_GUIDE.md, then read:
- kme_output/KNOWN_HAZARDS.md
- kme_output/ZKME_CHANGE_IMPACT.json
- kme_output/ZKME_PATHS.json
- kme_output/static/call_graph.json

Bug: [Users get a 500 error when submitting the registration form]
Analyze the bug using the artifacts. Identify the root cause,
assess blast radius, and propose a safe fix with minimal side effects.
Cite which artifacts informed each part of your analysis.
```

---

## Feature Planning / Requirements

### Workflow

1. **Understand the codebase** — Read `SYSTEM_OVERVIEW.md` for repo scale,
   languages, and tech stack.
2. **Find related features** — Search `FEATURE_INDEX.md` or `ZKME_FEATURE_REGISTRY.json`
   for existing features similar to what you're building.
3. **Map the API surface** — Read `INTERFACE_CATALOG.json` or `static/routes_detected.json`
   to understand existing endpoints you might extend.
4. **Understand entry points** — Read `L2_CONTEXT.md` for entry points, data models,
   call chains, and configuration.
5. **Check constraints** — Read `ZKME_CONTRACTS_INVARIANTS.json` for rules the new
   feature must respect (invariants, contracts, implicit rules).
6. **Examine data models** — Read `static/schemas.json` for existing data models
   you might need to extend.
7. **Check database** — Read `static/database_schema.json` for existing tables
   and migrations. *(not available in this scan)*

### Key Artifacts

| Artifact | What It Tells You |
|----------|-------------------|
| `SYSTEM_OVERVIEW.md` | Repo scale, languages, tech stack, interfaces | available |
| `L2_CONTEXT.md` | Entry points, data models, call chains, config | available |
| `INTERFACE_CATALOG.json` | All API endpoints with methods, paths, params | available |
| `ZKME_FEATURE_REGISTRY.json` | Existing features with core files | available |
| `FEATURE_INDEX.md` | Keyword-searchable feature finder | not generated |
| `ZKME_CONTRACTS_INVARIANTS.json` | Rules that must be preserved | available |
| `static/schemas.json` | Data models / schemas | available |

### Example Prompts

```
Read kme_output/ZKME_DEV_GUIDE.md, then read:
- kme_output/SYSTEM_OVERVIEW.md
- kme_output/L2_CONTEXT.md
- kme_output/ZKME_FEATURE_REGISTRY.json
- kme_output/ZKME_CONTRACTS_INVARIANTS.json
- kme_output/INTERFACE_CATALOG.json

Feature: [Add password reset flow via email]
Plan this feature: identify where it fits in the existing architecture,
which files to modify, which contracts/invariants to respect,
and which existing features it interacts with.
Cite which artifacts informed each decision.
```

---

## Refactoring / Task Execution

### Workflow

1. **Assess blast radius FIRST** — Read `ZKME_CHANGE_IMPACT.json` to understand
   what breaks if you change the target files.
2. **Check invariants** — Read `ZKME_CONTRACTS_INVARIANTS.json` for rules that
   must be preserved during the refactor.
3. **Understand inheritance** — Read `static/hierarchy.json` to see class
   inheritance chains (what extends what, what overrides what).
4. **Trace call edges** — Read `static/call_graph.json` to find all callers
   and callees of the functions you're changing.
5. **Map imports** — Read `static/import_edges.json` to find every file that
   imports from the module you're refactoring.
6. **Pre-change checklist** — Read `ZKME_PATCH_PLANNING_PACK.md` for a
   structured checklist before making changes.
7. **Risk signals** — Read `GIT_LEARNING/10_HOT_FILES.csv` for files that
   change frequently (higher risk). Read `GIT_LEARNING/11_CO_CHANGE_COUPLING.csv`
   for files that tend to change together (don't forget the pair).

### Key Artifacts

| Artifact | What It Tells You |
|----------|-------------------|
| `ZKME_CHANGE_IMPACT.json` | 2-hop blast radius for any file change | available |
| `ZKME_CONTRACTS_INVARIANTS.json` | Invariants that must be preserved | available |
| `static/hierarchy.json` | Class inheritance chains | available |
| `static/call_graph.json` | Function-level call edges | available |
| `static/import_edges.json` | File-level import/dependency graph | available |
| `ZKME_PATCH_PLANNING_PACK.md` | Pre-change checklist | available |

### Example Prompts

```
Read kme_output/ZKME_DEV_GUIDE.md, then read:
- kme_output/ZKME_CHANGE_IMPACT.json
- kme_output/ZKME_CONTRACTS_INVARIANTS.json
- kme_output/static/call_graph.json
- kme_output/static/import_edges.json
- kme_output/static/hierarchy.json

Task: [Rename UserService to AccountService across the codebase]
Analyze blast radius, identify all files that need updating,
check for inheritance/interface impacts, and produce a safe
change plan that preserves all invariants.
```

---

## Code Review

### Workflow

1. **Check hazards** — Does the change touch a known hazard area?
   Read `KNOWN_HAZARDS.md`.
2. **Verify blast radius** — Does the PR address all affected files?
   Read `ZKME_CHANGE_IMPACT.json`.
3. **Check invariants** — Are contracts preserved?
   Read `ZKME_CONTRACTS_INVARIANTS.json`.
4. **Auth rules** — Are authorization rules respected?
   Read `static/auth_contract.v1.json`.
5. **Test coverage** — Are changed areas covered by tests?
   Read `static/assertion_anchors.v1.json`.
6. **Golden paths** — Does the change break any end-to-end flow?
   Read `ZKME_PATHS.json`.

### Example Prompts

```
Read kme_output/ZKME_DEV_GUIDE.md, then read:
- kme_output/KNOWN_HAZARDS.md
- kme_output/ZKME_CHANGE_IMPACT.json
- kme_output/ZKME_CONTRACTS_INVARIANTS.json
- kme_output/static/auth_contract.v1.json
- kme_output/static/assertion_anchors.v1.json

Review this PR: [PR description or diff]
Check for: hazard area violations, blast radius coverage,
contract/invariant preservation, auth rule compliance,
and test coverage gaps. Cite artifacts for each finding.
```

---

## Test Planning

### Workflow

1. **Map user flows** — Read `static/flow_graph.v1.json` for end-to-end
   user flow graph.
2. **Negative scenarios** — Read `static/negative_test_matrix.v1.json` for
   pre-generated negative test scenarios.
3. **Data combinations** — Read `static/data_matrix.v1.json` for data
   combination matrices for parameterized tests.
4. **Existing coverage** — Read `static/assertion_anchors.v1.json` for
   existing test assertion locations (find gaps).
5. **Auth rules** — Read `static/auth_contract.v1.json` for authorization
   rules that need test coverage.
6. **UI-to-API bindings** — Read `static/ui_event_bindings.v1.json` for
   which UI actions trigger which API calls.

> **For ZeuZ test case generation**: Read `ZEUZ_TEST_GUIDE.md` instead —
> it has the complete tc.json format, row patterns, and ZeuZ-specific instructions.

### Example Prompts

```
Read kme_output/ZKME_DEV_GUIDE.md, then read:
- kme_output/static/flow_graph.v1.json
- kme_output/static/negative_test_matrix.v1.json
- kme_output/static/data_matrix.v1.json
- kme_output/static/assertion_anchors.v1.json

Feature: [User registration]
Plan comprehensive tests for this feature:
- Happy path scenarios from the flow graph
- Negative scenarios from the negative test matrix
- Boundary conditions from the data matrix
- Identify coverage gaps from assertion anchors
```

---

## Complete Artifact Reference

| Artifact | Purpose | Trust Level |
|----------|---------|-------------|
| `SYSTEM_OVERVIEW.md` | Repo scale, tech stack, interfaces | Authoritative | available |
| `KNOWN_HAZARDS.md` | Sensitive areas that could break | Authoritative | available |
| `L2_CONTEXT.md` | Entry points, data models, call chains, config | Authoritative | available |
| `FEATURE_INDEX.md` | Keyword-searchable feature finder | Authoritative | not generated |
| `INTERFACE_CATALOG.json` | All API endpoints | Authoritative | available |
| `ZKME_FEATURE_REGISTRY.json` | Existing features with core files | Authoritative | available |
| `ZKME_CHANGE_IMPACT.json` | 2-hop blast radius graph | Authoritative | available |
| `ZKME_CONTRACTS_INVARIANTS.json` | Invariants and contracts | Authoritative | available |
| `ZKME_PATHS.json` | Golden paths (interface → call → DB) | Authoritative | available |
| `ZKME_PATCH_PLANNING_PACK.md` | Pre-change checklist | Authoritative | available |
| `static/hot_files.json` | Most-changed files ranked | Authoritative | available |
| `static/import_edges.json` | File-level dependency graph | Authoritative | available |
| `static/call_graph.json` | Function-level call edges | Authoritative | available |
| `static/hierarchy.json` | Class inheritance chains | Authoritative | available |
| `static/routes_detected.json` | API routes | Authoritative | available |
| `static/frontend_calls.json` | Frontend-to-backend API calls | Authoritative | available |
| `static/schemas.json` | Data models / schemas | Authoritative | available |
| `static/database_schema.json` | DB schema and migrations | Authoritative | not generated |
| `static/flow_graph.v1.json` | End-to-end user flow graph | Authoritative | available |
| `static/negative_test_matrix.v1.json` | Negative test scenarios | Authoritative | available |
| `static/data_matrix.v1.json` | Data combinations for tests | Authoritative | available |
| `static/assertion_anchors.v1.json` | Existing test assertions | Authoritative | available |
| `static/auth_contract.v1.json` | Authorization rules | Authoritative | available |
| `static/ui_event_bindings.v1.json` | UI-to-API event bindings | Authoritative | available |
| `GIT_LEARNING/` | Git history signals (hot files, co-change) | Guidance only | available |
| `ZKME_CONTEXT_PACK/` | Tiered summaries (Tier1, Tier2, Tier3) | Authoritative | not generated |
| `ZEUZ_TEST_GUIDE.md` | ZeuZ tc.json generation guide | Reference | available |

---

## Rules

1. **`static/` is authoritative.** These files contain deterministic facts from the scan.
   Never contradict them. If a fact from `GIT_LEARNING/` conflicts with `static/`, the static file wins.
2. **Cite your sources.** For every file you change or recommendation you make,
   list which artifact(s) you used.
3. **Mark unknowns.** If you cannot prove a claim from the artifacts or source code,
   write **UNKNOWN** rather than guessing.
4. **Use artifacts before proposing changes.** Read the relevant artifacts first,
   then propose changes informed by the evidence.
5. **Respect invariants.** Read `ZKME_CONTRACTS_INVARIANTS.json` before any change
   to ensure you don't violate existing contracts.

---

*Generated by ZKME scan. For the full CLI: `zkme scan . --help`*
