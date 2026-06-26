# Visual And Accessibility Verification

For every UI feature change, produce evidence for the states that users actually experience.

## Visual States

- Default, hover, active, focus-visible, disabled, loading, empty, partial data, error, denied/unauthorized, and success.
- Mobile, tablet, and desktop layouts for screens affected by the change.
- Long text, translated text, large numbers, and missing optional data.

## Accessibility

- Keyboard navigation order is logical.
- Focus is visible and never trapped outside intentional dialogs.
- Controls have accessible names.
- Form errors are programmatically associated with fields.
- Dialogs and menus expose correct roles, labels, and escape/close behavior.
- Color is not the only signal for status or validation.

## Evidence

Use Playwright screenshots, traces, and accessibility assertions where possible. Store durable evidence paths in the relevant manual case, portable testcase, or ZeuZ-compatible report.
