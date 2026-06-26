# API Tests

AI agents must add or update API tests when routes, controllers, schemas, DTOs, auth behavior, status codes, pagination, filtering, exports, or integration contracts change.

## Rules

- Use detected routes and source contracts. Do not invent endpoints.
- Test success and negative cases.
- Preserve existing error shapes unless a contract change was approved.
- Test unauthenticated, forbidden, invalid input, not found, conflict, rate limit, and partial result paths when relevant.
- Keep requests deterministic and isolated.

## Detected Commands

- No build, test, lint, or typecheck command was detected. Use UNKNOWN instead of inventing one.
