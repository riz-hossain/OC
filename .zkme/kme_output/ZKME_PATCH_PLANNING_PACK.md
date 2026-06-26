# ZKME Patch Planning Pack

**snapshot_digest**: `f6d78848769d95ee2343c33a8966fa3ab720695c`

Use this template BEFORE generating code with any LLM.
It forces a design-first workflow and aligns changes with ZKME artifacts.

## 1) Target
- Feature name (from `ZKME_FEATURE_REGISTRY.json`): 
- Entry point (route/CLI/job) to start from: 
- Bug / Feature request summary: 

## 2) Files to Touch (ranked + justification)
- `orange_circle_platformer.html` — (why?)
- `README.md` — (why?)

## 3) Blast Radius (what could break)
- Consult `ZKME_CHANGE_IMPACT.json` for the target file(s)
- List dependent modules, shared utilities, config, schema impacts

## 4) Contracts & Invariants (must not violate)
- Consult `ZKME_CONTRACTS_INVARIANTS.json`
- List required validations/authz/state rules

## 5) Golden/Failure Paths (preserve behavior)
- Consult `ZKME_PATHS.json` for the entry point
- Note expected success flow + error/fallback behaviors

## 6) Tests
- Tests to update/add: 
- Tests to run: 

## 8) Patch Steps
1. 
2. 
3. 

## 9) Review Checklist
- [ ] Changes are limited to files justified by ZKME artifacts
- [ ] Contracts/invariants are preserved
- [ ] Error handling behavior preserved (failure paths)
- [ ] Tests updated/added and executed
