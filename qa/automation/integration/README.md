# Integration Tests

Use this area for service, database, worker, queue, and cross-module behavior that cannot be proven with a unit test alone.

## Rules

- Prefer the repo's existing integration test pattern.
- Keep setup and teardown explicit.
- Use local containers, mocks, or fixtures instead of live external services by default.
- Preserve auth, tenant, and data-isolation checks.
- Add rollback or cleanup when data changes.
