# Mobile Automation

Not applicable: no mobile surfaces were detected by ZKME.

When applicable, mobile checks should cover startup, low-memory behavior, poor-network or offline behavior, UI-thread blocking, critical navigation, and accessibility labels.

Local runner integration is configured in `qa/automation/config/zkme-adapters.json` under `adapters.mobile`.

The default adapter can use Appium directly when enabled with `remoteUrl` and `capabilities`, or run a project-specific command that receives a `zkme.adapter-step-request.v1` JSON payload on stdin.
