# ZKME AI Adapter Bridge

This repository is governed by ZKME-generated project instructions.

Read these before implementing, changing, or reviewing code:

1. `.zkme/generated-governance/AGENTS.generated.md`
2. `.zkme/generated-governance/DEVELOPMENT_STANDARDS.md`
3. `.zkme/generated-governance/UI_UX_STANDARDS.md`
4. `.zkme/generated-governance/QA_AUTOMATION_STANDARDS.md`
5. `qa/AI_TEST_GENERATION_CONTRACT.md`
6. `qa/feature-architecture-map.json`
7. `qa/test-oracles.json`
8. `qa/test-data-matrix.json`
9. `qa/traceability-matrix.json`
10. `qa/test-design-quality.json`
9. `qa/automation/README.md`

Hard rules:

- Every feature change must update manual and automated QA evidence.
- Manual cases must meet or exceed the lead-QA model in `qa/test-design-quality.json`; shallow happy-path-only cases are not acceptable.
- UI changes must reuse existing components, design tokens, and patterns before adding new UI primitives.
- Cross-surface behavior must produce portable testcases under `qa/automation/local-runner/test-cases/` and ZeuZ-compatible drafts under `qa/automation/zeuz/test-cases/`.
- Local reports must preserve ZeuZ-compatible `zeuzExecutionLog` output under `qa/automation/reports/zeuz-compatible/`.
- Run `python qa/automation/validate_test_design_quality.py` and `python qa/automation/verify_zkme_qa_contract.py` before handing off feature work.
