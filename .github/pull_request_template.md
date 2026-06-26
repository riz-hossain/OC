## ZKME QA Checklist

- [ ] I read `.zkme/generated-governance/AGENTS.generated.md` and the relevant generated standards.
- [ ] Manual acceptance cases were added or updated under `qa/manual/test-cases/`.
- [ ] Unit/API/DB/mobile/desktop/performance/security tests were added or explicitly marked not applicable.
- [ ] Web UI changes reuse existing components/tokens and have Playwright or visual/accessibility evidence.
- [ ] Cross-surface behavior has a portable testcase under `qa/automation/local-runner/test-cases/`.
- [ ] ZeuZ-compatible draft/result paths were updated when automation changed.
- [ ] `python qa/automation/verify_zkme_qa_contract.py` passes.
- [ ] `python qa/automation/validate_ai_adapters.py` passes.

## Notes

Link the generated manual, portable, Playwright, ZeuZ, and report artifacts that prove the change.
