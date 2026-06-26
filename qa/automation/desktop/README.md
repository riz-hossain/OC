# Desktop Automation

Use this folder only when desktop surfaces are detected or the user explicitly requests desktop automation.

Local runner integration is configured in `qa/automation/config/zkme-adapters.json` under `adapters.desktop`.

Desktop steps should use a project-specific command adapter for WinAppDriver, pywinauto, AppleScript, Sikuli, ZeuZ desktop actions, or an internal desktop harness. Do not invent desktop selectors or image targets without evidence.
