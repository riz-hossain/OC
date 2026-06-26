# Portable Testcase Examples

Portable testcases are the canonical source for generated cross-surface tests.

## Playwright Step

```json
{
  "id": "open-login",
  "stepKey": "open-login",
  "stepName": "Open login page",
  "intent": "Open login page",
  "adapter": "playwright",
  "action": "navigate",
  "input": {"url": "/login"},
  "expected": "Login page is visible",
  "zeuzMapping": {
    "stepKey": "open-login",
    "stepName": "Open login page",
    "stepSequence": 1,
    "stepId": 1,
    "actionType": "playwright action",
    "actionLabel": "go to link",
    "actionName": "go to link",
    "rows": [["/login", "url", ""]]
  }
}
```

## API Step

```json
{
  "id": "get-profile",
  "stepKey": "get-profile",
  "stepName": "Fetch the current user profile",
  "intent": "Fetch the current user profile",
  "adapter": "api",
  "action": "GET",
  "input": {
    "method": "GET",
    "url": "/api/profile",
    "expectedStatus": 200,
    "expectedContains": "email"
  },
  "expected": "Profile response includes user email"
}
```

## SQLite DB Step

```json
{
  "id": "verify-user-row",
  "stepKey": "verify-user-row",
  "stepName": "Verify user exists in local sqlite database",
  "intent": "Verify user exists in local sqlite database",
  "adapter": "db",
  "action": "select query",
  "input": {
    "driver": "sqlite",
    "database": "tmp/test.db",
    "sql": "select id from users where email = ?",
    "params": ["%|user_email|%"],
    "expectedRows": 1
  },
  "expected": "One matching user row exists"
}
```

## Mobile Candidate

```json
{
  "id": "mobile-login-visible",
  "stepKey": "mobile-login-visible",
  "stepName": "Validate mobile login screen",
  "intent": "Validate mobile login screen",
  "adapter": "mobile",
  "action": "validate partial text",
  "selector": "login-title",
  "expected": "Login screen is visible",
  "zeuzMapping": {
    "stepKey": "mobile-login-visible",
    "stepName": "Validate mobile login screen",
    "stepSequence": 1,
    "stepId": 1,
    "actionType": "appium action",
    "actionLabel": "validate partial text",
    "actionName": "Validate_Text_Appium",
    "rows": [["login-title", "element parameter", ""], ["Login", "input parameter", ""]]
  }
}
```

Mobile and desktop candidates are intentionally skipped by the default runner until a project-specific device/session adapter is configured.
