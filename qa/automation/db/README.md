# Database Tests

Use this folder for database migration, query, fixture, and data-integrity test notes or generated assets.

## Rules

- Use approved local or containerized databases.
- Never run generated DB tests against production.
- Test empty, duplicate, malformed, boundary, permission, tenant-isolation, and rollback/cleanup paths where relevant.
- ZeuZ DB action candidates belong under `qa/automation/zeuz/` when the workflow spans DB plus another surface.
