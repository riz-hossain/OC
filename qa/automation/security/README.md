# Security Automation

Use this folder for safe local security checks: dependency auditing, SAST, configuration validation, authZ/authN assertions, input validation, and non-destructive API probes.

Local runner integration is configured in `qa/automation/config/zkme-adapters.json` under `adapters.security`.

Rules:

- Never run destructive or production-targeting security scans from generated tests.
- Keep credentials out of testcase JSON; use environment variables or a local secret manager.
- Adapter commands must print JSON with `status`, `message`, and optional `artifacts`.
