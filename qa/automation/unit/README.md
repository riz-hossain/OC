# Unit Tests

AI agents must add or update unit tests when feature work changes business logic, validation, parsing, formatting, state transitions, permissions helpers, utility functions, or error handling.

## Rules

- Use the existing project test framework and naming conventions.
- Keep unit tests close to the code when that is the repo pattern.
- Use deterministic fixtures.
- Cover success, failure, boundary, and permission-denied behavior where applicable.
- If unit tests are not applicable, record the reason in the feature final report.

## Detected Commands

- No build, test, lint, or typecheck command was detected. Use UNKNOWN instead of inventing one.
