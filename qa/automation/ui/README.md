# UI Automation And Consistency

This folder enforces the ZKME UI/UX rule: reuse the existing component system, design tokens, accessibility patterns, and visual verification flow before adding new UI primitives.

## Generated Tools

- `verify_ui_consistency.py`: scans source files, detects component libraries/design tokens, writes component inventory, and gates duplicate primitive systems.
- `VISUAL_ACCESSIBILITY_CHECKS.md`: required visual and accessibility verification guidance.
- `ui-exceptions.json`: explicit, reviewed exceptions for intentional duplicate primitives.

## Required For UI Work

- Run `python qa/automation/ui/verify_ui_consistency.py --write-inventory`.
- Add or update Playwright checks for critical flows.
- Verify keyboard, focus, accessible names, contrast-sensitive states, loading, empty, error, denied, success, and responsive layouts.
- Do not add a second `Button`, `Input`, `Card`, `Modal`, `Dialog`, `Select`, `Checkbox`, `Radio`, `Table`, `Toast`, or `Dropdown` system without documenting an exception.
