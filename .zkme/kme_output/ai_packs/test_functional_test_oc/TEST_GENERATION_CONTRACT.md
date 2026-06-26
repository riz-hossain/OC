# ZeuZ Test Case Generation Contract
## Version: 1.1 | ZKME-Generated | Surfaces: ui, desktop, db

---

## Task

Generate a complete ZeuZ test case in `tc.json` format for the following request.

**Test Title:** Functional Test - OC
**Objective:** Verify core functionality of OC. Navigate through primary flows, perform key actions, and validate expected application behaviour.
**Surfaces Required:** ui, desktop, db
**Capability Tags:** ui_navigate, ui_assert, desktop_action

- **Desktop surfaces detected**: For WPF, prefer `AutomationId` as the primary selector, `x:Name` as fallback. For WinForms, use `AccessibleName` or `Name` properties. Consider window/dialog lifecycle: ensure the target window is active before interacting.



---

## Output Format

```json
{
  "testCase": {
    "testCaseDetail": {
      "id": "TEST-XXXX",
      "name": "<test title>",
      "priority": "P2",
      "type": "",
      "localization": "Yes",
      "createdBy": 0,
      "creationDate": "YYYY-MM-DD 00:00:00 +0000 UTC",
      "modifiedBy": 0,
      "modifyDate": "YYYY-MM-DD 00:00:00 +0000 UTC",
      "testCaseType": "Automated",
      "time": "00:05:00",
      "automatability": "Automated",
      "preRequisite": null
    },
    "steps": [
      {
        "id": 1,
        "testCaseId": "TEST-XXXX",
        "stepId": 1,
        "name": "<Step Name>",
        "description": "<p>Step description</p>",
        "expected": "<p>Expected result</p>",
        "hasData": true,
        "verifyPoint": false,
        "continuePoint": false,
        "time": 30,
        "sequence": 1,
        "type": "normal",
        "stepInfo": {
          "description": "<p>Step description</p>",
          "driver": "Built_In_Driver",
          "stepType": "automated",
          "dataRequired": true,
          "stepFeature": "0",
          "stepEnable": true,
          "stepEditable": true,
          "caseDesc": "<p>Step description</p>",
          "expected": "<p>Expected result</p>",
          "verifyPoint": false,
          "stepContinue": false,
          "estdTime": "30",
          "automatable": "Desktop",
          "createdBy": "0",
          "createdDate": "YYYY-MM-DD 00:00:00",
          "modifiedBy": "0",
          "modifiedDate": "YYYY-MM-DD 00:00:00",
          "projectId": "PROJ-1",
          "teamId": "1",
          "alwaysRun": false,
          "runOnFail": false,
          "attachments": []
        },
        "actions": [
          {
            "id": 1,
            "stepId": 1,
            "name": "None",
            "rows": [
              {
                "id": 1,
                "data": ["<param_name>", "<sub_field>", "<value>"],
                "sequence": 1
              },
              {
                "id": 2,
                "data": ["<action_name>", "<zeuz_action_label>", "<action_name>"],
                "sequence": 2
              }
            ],
            "sequence": 1,
            "enabled": true
          }
        ]
      }
    ]
  }
}
```

---

## Action Row Patterns

---
### ZeuZ Row Block Structure
Every action in ZeuZ is expressed as a block of rows where:
- Parameter rows come first (element parameter, optional parameter, etc.)
- The FINAL row is ALWAYS the action identifier: `[action_name, zeuz_action_label, action_name]`

Each row has: `"data": [col1, col2, col3]`
- col1 = parameter name or action name
- col2 = sub_field type (see Sub-Field Type Reference below)
- col3 = value or action name again

### Sub-Field Type Reference
| col2 value              | When to use                                                        |
|-------------------------|--------------------------------------------------------------------|
| `element parameter`     | Primary UI element locator — finds ALL matching elements on page. Supports: `id`, `class`, `name`, `text`, `tag`, `data-*`, `aria-label`, `role`, `xpath`, `css`, `index`. Prefix with `*` for partial match, `**` for case-insensitive partial. |
| `unique parameter`      | Fast single-match locator — returns FIRST match and stops. Faster than `element parameter`. Cannot combine with parent/sibling/child/index. |
| `parent parameter`      | Parent element locator — disambiguates when target elements are identical but have different parents. |
| `sibling parameter`     | Sibling element locator — disambiguates when elements AND parents are identical but nearby siblings differ. |
| `child parameter`       | Child element locator — narrow search to children of a specific parent. |
| `sr element parameter`  | Shadow DOM element locator — for elements inside shadow roots. Only parent + element work (no sibling/child/text). |
| `sr parent parameter`   | Shadow DOM parent locator — parent element containing the shadow root. |
| `selenium action`       | Web UI actions (click, enter text, verify text, go to url, hover, wait, save text, save attribute, select by visible text) |
| `appium action`         | Mobile UI actions (tap, enter text, swipe, long press)             |
| `rest action`           | REST API actions (save response)                                   |
| `graphql`               | GraphQL query/mutation document body (col1 = "query")              |
| `database action`       | Database actions (select query, insert update delete query, connect to db) |
| `common action`         | Common actions (save into variable, sleep, compare variable, execute python code, log) |
| `utility action`        | Utility actions (run command, log 1)                               |
| `input parameter`       | Non-UI data inputs (db_type, db_host, db_port, db_name, db_user)  |
| `optional parameter`    | Optional settings (wait for status code, run in background, strip whitespaces, command separator) |
| `optional option`       | Element modifiers (allow hidden = yes)                             |
| `compare`               | Variable comparison (col1 = variable value, col3 = expected value) |
| `value`                 | Command/data values (col1 = "command", col3 = shell command text)  |
| `while loop`            | While loop start (col1 = "run actions", col3 = action range)      |
| `loop settings`         | Loop config (col1 = "repeat", col3 = max iterations)              |
| `optional loop settings`| Loop exit (col1 = "exit loop", col3 = condition)                   |
| `if else`               | Conditional (col1 = condition or "else", col3 = action jumps)      |
| `for loop action`       | For loop iteration                                                 |
| `save parameter`        | Save element attribute (col1 = attribute name, col3 = variable name) |

### UI Click Example

### Save Variable
```json
{"rows": [
  {"data": ["data",             "element parameter", "my_value"],    "sequence": 1},
  {"data": ["save into variable","common action",   "my_var_name"],  "sequence": 2}
]}
```
Use `%|my_var_name|%` in any subsequent row to reference the saved value.

---
### Web UI — Selenium

**Click element:**
```json
{"rows": [
  {"data": ["data-testid",  "element parameter", "login-submit-btn"], "sequence": 1},
  {"data": ["click",        "selenium action",   "click"],            "sequence": 2}
]}
```

**Enter text:**
```json
{"rows": [
  {"data": ["data-testid",  "element parameter", "email-input"],          "sequence": 1},
  {"data": ["text",         "element parameter", "user@example.com"],     "sequence": 2},
  {"data": ["enter text",   "selenium action",   "enter text"],           "sequence": 3}
]}
```

**Navigate to URL:**
```json
{"rows": [
  {"data": ["url",          "element parameter", "%|base_url|%/login"],   "sequence": 1},
  {"data": ["go to url",    "selenium action",   "go to url"],            "sequence": 2}
]}
```

**Verify text (assertion):**
```json
{"rows": [
  {"data": ["data-testid",  "element parameter", "welcome-banner"],       "sequence": 1},
  {"data": ["compare",      "element parameter", "Welcome back"],         "sequence": 2},
  {"data": ["verify text",  "selenium action",   "verify text"],          "sequence": 3}
]}

{
  "rows": [
    {"data": ["method",             "element parameter",  "POST"],              "sequence": 1},
    {"data": ["url",                "element parameter",  "/api/auth/login"],   "sequence": 2},
    {"data": ["body",               "element parameter",  "{\"username\": \"%|username|%\", \"password\": \"%|password|%\"}"], "sequence": 3},
    {"data": ["wait for status code","optional parameter", "200"],              "sequence": 4},
    {"data": ["save response",      "rest action",        "api_response"],      "sequence": 5}
  ]
}
```
Note: `["save response", "rest action", "<var>"]` is the action row that triggers REST execution and saves the response.
Optionally add `["wait for status code", "optional parameter", "200"]` before the action row to wait for a specific status.

### GraphQL Call Example
```json
{
  "rows": [
    {"data": ["method",             "element parameter",  "post"],               "sequence": 1},
    {"data": ["url",                "element parameter",  "https://%|host|%/service/graphql"], "sequence": 2},
    {"data": ["query",              "graphql",            "mutation { login(userName:\"fred\", password:\"pass\") { token } }"], "sequence": 3},
    {"data": ["wait for status code","optional parameter", "200"],               "sequence": 4},
    {"data": ["save response",      "rest action",        "auth_token"],         "sequence": 5}
  ]
}
```
**CRITICAL**: For GraphQL, col1 is `"query"` and col2 is `"graphql"` (NOT `"element parameter"`).
The `"save response"` / `"rest action"` row triggers execution and saves the response.

### Save Variable Example (3-Row Pattern)
```json
{
  "rows": [
    {"data": ["data",               "element parameter",  "%|some_value|%"],     "sequence": 1},
    {"data": ["operation",          "element parameter",  "save"],               "sequence": 2},
    {"data": ["save into variable", "common action",      "my_var_name"],        "sequence": 3}
  ]
}
```
**CRITICAL**: Save variable uses 3 rows: `data` → `operation` (save) → `save into variable`.

### Compare Variable Example
```json
{
  "rows": [
    {"data": ["%|cmd_output['return_code']|%", "compare",       "0"],            "sequence": 1},
    {"data": ["compare variable",              "common action", "exact match"],  "sequence": 2}
  ]
}
```

**Verify element visible:**
```json
{
  "rows": [
    {"data": ["data-testid",    "element parameter", "dashboard-header"],   "sequence": 1},
    {"data": ["compare",        "element parameter", "Welcome"],            "sequence": 2},
    {"data": ["verify text",    "selenium action",   "verify text"],        "sequence": 3}
  ]
}
```

### Sleep Example
```json
{
  "rows": [
    {"data": ["sleep", "common action", "3"], "sequence": 1}
  ]
}
```

### Execute Python Code Example
```json
{
  "rows": [
    {"data": ["execute python code", "common action", "sr.Set_Shared_Variables(\"key\", value)"], "sequence": 1}
  ]
}
```

### Run Command Example
```json
{
  "rows": [
    {"data": ["command",          "value",              "docker ps -a"],  "sequence": 1},
    {"data": ["run in background","optional parameter", "false"],         "sequence": 2},
    {"data": ["strip whitespaces","optional parameter", "true"],          "sequence": 3},
    {"data": ["command separator","optional parameter", "&&"],            "sequence": 4},
    {"data": ["run command",      "utility action",     "cmd_output"],    "sequence": 5}
  ]
}
```

### Log Message Example
```json
{
  "rows": [
    {"data": ["log 1", "utility action", "Step completed successfully"], "sequence": 1}
  ]
}
```

### While Loop Example
```json
{
  "rows": [
    {"data": ["run actions",  "while loop",             "next,next+1"],    "sequence": 1},
    {"data": ["exit loop",    "optional loop settings",  "if next pass"],  "sequence": 2},
    {"data": ["repeat",       "loop settings",           "30"],            "sequence": 3}
  ]
}
```

### If/Else Conditional Example
```json
{
  "rows": [
    {"data": ["if project == 'Advance'", "if else", "next, next+2"],  "sequence": 1},
    {"data": ["else",                    "if else", "next+1, next+2"],"sequence": 2}
  ]
}
```
The col3 values specify action jumps: `"next"` = run next action, `"next+N"` = skip N actions, `"fail"` = fail the step.

### DB Connect + Query Example
```json
{
  "rows": [
    {"data": ["db_type",      "input parameter",  "postgres"],                "sequence": 1},
    {"data": ["db_host",      "input parameter",  "%|db_host|%"],             "sequence": 2},
    {"data": ["db_port",      "input parameter",  "5432"],                    "sequence": 3},
    {"data": ["db_name",      "input parameter",  "%|db_name|%"],             "sequence": 4},
    {"data": ["db_user",      "input parameter",  "%|db_user|%"],             "sequence": 5},
    {"data": ["db_password",  "input parameter",  "%|db_password|%"],         "sequence": 6},
    {"data": ["connect to db","database action",  "connect to db"],           "sequence": 7}
  ]
}
```

### DB Select Query Example
```json
{
  "rows": [
    {"data": ["query",         "input parameter",  "SELECT * FROM users WHERE email = '%|email|%'"], "sequence": 1},
    {"data": ["select query",  "database action",  "db_result"],  "sequence": 2}
  ]
}
```
Note: The SQL goes in a `query|input parameter` row. The `select query|database action|var_name` row triggers execution and saves results into the variable.

### DB Insert/Update/Delete Query Example
```json
{
  "rows": [
    {"data": ["query",                      "input parameter",  "INSERT INTO users (email, name) VALUES ('%|email|%', '%|name|%')"], "sequence": 1},
    {"data": ["insert update delete query", "database action",  "db_result"],  "sequence": 2}
  ]
}
```
Note: Use `insert update delete query` as the action for any write operation (INSERT, UPDATE, DELETE). Same 2-row pattern as select query.

### Wait for Element Example
```json
{
  "rows": [
    {"data": ["data-testid", "element parameter", "Header.dashboard"], "sequence": 1},
    {"data": ["wait",        "selenium action",   "60"],               "sequence": 2}
  ]
}
```
Note: col3 is the timeout in seconds. Waits until the element identified by the parameter rows appears on page.

### Save Element Text Example
```json
{
  "rows": [
    {"data": ["data-testid", "element parameter", "total-count"],      "sequence": 1},
    {"data": ["save text",   "selenium action",   "saved_text_var"],   "sequence": 2}
  ]
}
```
Note: Saves the visible text content of the matched element into a variable. Access later with `%|saved_text_var|%`.

### Save Element Attribute Example
```json
{
  "rows": [
    {"data": ["data-testid",    "element parameter", "user-link"],     "sequence": 1},
    {"data": ["href",           "save parameter",    "link_url"],      "sequence": 2},
    {"data": ["save attribute", "selenium action",   "save attribute"],"sequence": 3}
  ]
}
```
Note: col1 of the `save parameter` row is the HTML attribute name (href, value, src, etc.), col3 is the variable name.

### Hover Example
```json
{
  "rows": [
    {"data": ["data-testid", "element parameter", "menu-dropdown"], "sequence": 1},
    {"data": ["hover",       "selenium action",   "hover"],         "sequence": 2}
  ]
}
```

### Select Dropdown by Visible Text Example
```json
{
  "rows": [
    {"data": ["data-testid",           "element parameter", "priority-dropdown"], "sequence": 1},
    {"data": ["select by visible text","selenium action",   "P1"],                "sequence": 2}
  ]
}
```

### For Loop Example
```json
{
  "rows": [
    {"data": ["run actions",            "for loop action",        "next,next+1"], "sequence": 1},
    {"data": ["for col in %|data|%",    "loop settings",          "col"],         "sequence": 2},
    {"data": ["exit loop",              "optional loop settings",  "if next pass"],"sequence": 3},
    {"data": ["repeat",                 "loop settings",           "100"],         "sequence": 4}
  ]
}
```
Note: For loops iterate over a list variable. col1 of the `for` row defines the iterator variable.

### Mobile Tap Example (Appium)
For mobile surfaces, use `appium action` instead of `selenium action`:
```json
{
  "rows": [
    {"data": ["testID", "element parameter", "login_submit_btn"], "sequence": 1},
    {"data": ["tap", "appium action", "tap"], "sequence": 2}
  ]
}
```

### Mobile Swipe Example (Appium)
```json
{
  "rows": [
    {"data": ["swipe", "appium action", "up"], "sequence": 1}
  ]
}
```

### Mobile Text Input Example (Appium)
```json
{
  "rows": [
    {"data": ["testID", "element parameter", "username_input"], "sequence": 1},
    {"data": ["test", "element parameter", "testuser@example.com"], "sequence": 2},
    {"data": ["enter text", "appium action", "enter text"], "sequence": 3}
  ]
}
```

### Desktop Click Example (WPF/WinForms)
For desktop surfaces, use `AutomationId` or `Name` as selectors:
```json
{
  "rows": [
    {"data": ["AutomationId", "element parameter", "btnSubmit"], "sequence": 1},
    {"data": ["click", "selenium action", "click"], "sequence": 2}
  ]
}
```

### Save Attribute Values in List (Bulk Data Extraction)
Extracts multiple attribute values from child elements under a parent, with filtering:
```json
{
  "rows": [
    {"data": ["data-testid", "element parameter", "product-list-container"], "sequence": 1},
    {"data": ["attributes", "target parameter", "class=\"product-name\",\nreturn=\"text\""], "sequence": 2},
    {"data": ["attributes", "target parameter", "class=\"product-price\",\nreturn=\"text\",\nreturn_does_not_contain=\"0.00\""], "sequence": 3},
    {"data": ["save attribute values in list", "selenium action", "products"], "sequence": 4}
  ]
}
```
**target parameter syntax**: `attr="value"` locates child elements. `return="text|id|href|src|tag|checked|<any-attr>"` = what to extract.
`return_contains="keyword"` / `return_does_not_contain="exclude"` = filters. Multiple target parameters create paired 2D list.

### Extract Table Data (with row/column filters)
```json
{
  "rows": [
    {"data": ["tag", "element parameter", "tbody"], "sequence": 1},
    {"data": ["row", "optional parameter", "0-10"], "sequence": 2},
    {"data": ["column", "optional parameter", "0,1,3"], "sequence": 3},
    {"data": ["extract table data", "selenium action", "table_var"], "sequence": 4}
  ]
}
```
Row/column optional parameters are filters (ranges or comma-separated indices). Omit for all.

### If Element Exists (Conditional Variable)
```json
{
  "rows": [
    {"data": ["data-testid", "element parameter", "error-banner"], "sequence": 1},
    {"data": ["if element exists", "selenium action", "true = has_error"], "sequence": 2}
  ]
}
```
col3 format: `value = variable_name`. Sets variable to value if found, `"false"` if not.

### Classifier AI (Last-Resort AI Action)
```json
{
  "rows": [
    {"data": ["category", "input parameter", "success/failure"], "sequence": 1},
    {"data": ["text", "input parameter", "Natural language description"], "sequence": 2},
    {"data": ["classifier ai", "common action", "result_variable"], "sequence": 3}
  ]
}
```
**LAST RESORT ONLY.** Uses NLP for best-effort classification when deterministic selectors fail.

---
### Database

**Execute SELECT query:**
```json
{"rows": [
  {"data": ["query",        "element parameter", "SELECT status FROM orders WHERE id = '%|order_id|%'"], "sequence": 1},
  {"data": ["execute query","database action",   "execute query"],                                       "sequence": 2}
]}
```

**SELECT and save result into variable (for later assertions):**
```json
{"rows": [
  {"data": ["query",        "element parameter", "SELECT status, created_at FROM orders WHERE id = '%|order_id|%'"], "sequence": 1},
  {"data": ["save result",  "element parameter", "db_order"],                                                         "sequence": 2},
  {"data": ["execute query","database action",   "execute query"],                                                     "sequence": 3}
]}
```
→ Access result fields: `%|db_order[0].status|%`, `%|db_order[0].created_at|%`
→ Row 0 = first result row; subsequent rows indexed as `%|db_order[1].field|%`

**Verify DB result matches expected value:**
```json
{"rows": [
  {"data": ["query",        "element parameter", "SELECT status FROM orders WHERE id = '%|order_id|%'"], "sequence": 1},
  {"data": ["save result",  "element parameter", "db_check"],                                             "sequence": 2},
  {"data": ["compare",      "element parameter", "CONFIRMED"],                                            "sequence": 3},
  {"data": ["column",       "element parameter", "status"],                                               "sequence": 4},
  {"data": ["execute query","database action",   "execute query"],                                         "sequence": 5}
]}
```

**Execute INSERT (setup data):**
```json
{"rows": [
  {"data": ["query",        "element parameter", "INSERT INTO test_users (email, role) VALUES ('test@example.com', 'viewer')"], "sequence": 1},
  {"data": ["execute query","database action",   "execute query"],                                                              "sequence": 2}
]}
```

**Execute DELETE (cleanup):**
```json
{"rows": [
  {"data": ["query",        "element parameter", "DELETE FROM test_users WHERE email = 'test@example.com'"], "sequence": 1},
  {"data": ["execute query","database action",   "execute query"],                                           "sequence": 2}
]}
```

DB variable chaining rules:
- `"save result"` stores the full result set as a list of row dicts
- Access fields: `%|db_var[row_index].column_name|%`  (row_index starts at 0)
- Use `%|db_var[0].id|%` in subsequent REST/Selenium/Appium rows to chain DB data forward

---
### Multi-Surface E2E Chaining (Cross-Layer Tests)

**The core pattern: Save → Reuse Across Surfaces**

ZeuZ variable syntax `%|variable_name|%` works in ANY surface (REST, Selenium, Appium, DB).

**E2E Pattern: GraphQL Auth → REST call with token → Selenium assert → DB validate**

Step 1 — Authenticate (GraphQL), save token:
```json
{"rows": [
  {"data": ["method",   "element parameter", "POST"],                  "sequence": 1},
  {"data": ["url",      "element parameter", "%|base_url|%/service/graphql"], "sequence": 2},
  {"data": ["graphql",  "element parameter", "mutation Login($u:String!,$p:String!){login(u:$u,p:$p){token}}"], "sequence": 3},
  {"data": ["u",        "graphql variable",  "%|username|%"],          "sequence": 4},
  {"data": ["p",        "graphql variable",  "%|password|%"],          "sequence": 5},
  {"data": ["save under","rest action",      "auth_token"],            "sequence": 6}
]}
```
→ `%|auth_token|%` is now available to all subsequent steps.

Step 2 — Call protected REST endpoint, save result:
```json
{"rows": [
  {"data": ["method",        "element parameter", "POST"],             "sequence": 1},
  {"data": ["url",           "element parameter", "%|base_url|%/api/orders"], "sequence": 2},
  {"data": ["Authorization", "headers",           "Bearer %|auth_token|%"], "sequence": 3},
  {"data": ["body",          "element parameter", "{"item_id": "%|item_id|%"}"], "sequence": 4},
  {"data": ["save under",    "rest action",       "order_response"],   "sequence": 5}
]}
```
→ `%|order_response.order_id|%` available for DB and UI steps.

Step 3 — Verify in UI (Selenium):
```json
{"rows": [
  {"data": ["url",          "element parameter", "%|base_url|%/orders/%|order_response.order_id|%"], "sequence": 1},
  {"data": ["go to url",    "selenium action",   "go to url"],         "sequence": 2}
]},
{"rows": [
  {"data": ["data-testid",  "element parameter", "order-status"],      "sequence": 1},
  {"data": ["compare",      "element parameter", "CONFIRMED"],         "sequence": 2},
  {"data": ["verify text",  "selenium action",   "verify text"],       "sequence": 3}
]}
```

Step 4 — Verify in DB:
```json
{"rows": [
  {"data": ["query",        "element parameter", "SELECT status FROM orders WHERE id = '%|order_response.order_id|%'"], "sequence": 1},
  {"data": ["execute query","database action",   "execute query"],     "sequence": 2}
]}
```

**Variable chaining rules:**
1. `save under` (REST/GraphQL) saves the full JSON response — access fields with `%|var.field|%`
2. `save into variable` (common) saves a literal value or expression
3. Variables flow forward only — each step can use variables from all prior steps
4. Same variables work across surfaces: REST → Selenium → Appium → DB
5. Init step should always store: `%|base_url|%`, `%|username|%`, `%|password|%`

---
## ZeuZ Variable Syntax Reference

### Basic Variable Injection
`%|variable_name|%` — injects a saved variable anywhere (col1, col2, or col3).

### Field Access (dot notation)
```
%|response.id|%           — access "id" field of a saved JSON/dict
%|auth_result.token|%     — nested: token from auth response
%|soap_dict.Envelope.Body.OrderResponse.Id|%  — deep SOAP XML path
```

### Array / List Indexing
```
%|db_result[0].status|%   — first row, "status" column
%|db_result[1].email|%    — second row, "email" column
%|items[0].name|%         — first item in a list
```

### Dict Key Access
```
%|config["base_url"]|%    — string key lookup
%|headers["Authorization"]|%
```

### Type Conversion Functions
```
%|num(price)|%            — convert saved variable to number
%|str(order_id)|%         — convert to string
%|len(items)|%            — length of a list
```

### Common Built-in Variables
| Variable          | Set by                         | Meaning                     |
|-------------------|--------------------------------|-----------------------------|
| `%|base_url|%`    | Init step / environment        | Application base URL        |
| `%|username|%`    | Init step / test data          | Login username              |
| `%|password|%`    | Init step / test data          | Login password              |
| `%|auth_token|%`  | `save under` after login step  | Bearer token from auth      |
| `%|db_result[0].field|%` | `save result` after DB query | DB row field         |

### Rules
1. Variables are WRITE-ONCE per step — later steps can overwrite if they save to the same name.
2. All surfaces (REST, Selenium, Appium, DB, SOAP) can read any variable saved by a prior step.
3. If a variable does not exist at runtime, ZeuZ raises an error — never reference a variable before it is saved.
4. Prefer descriptive names: `auth_token` not `t`, `order_response` not `r`.


---

## Selector Priority Rules (STATIC RULE — Never Override)

Use the highest-priority selector available for each element, in this order:
1. `data-automation`  — confidence: 0.40 (highest)
2. `data-testid`      — confidence: 0.30
3. `data-test`        — confidence: 0.30
4. `aria-label`       — confidence: 0.30
5. `id`               — confidence: 0.20
6. `name`             — confidence: 0.20
7. `text`             — confidence: 0.15 (visible text content of the element)
8. `tag`              — confidence: 0.10 (HTML tag name — combine with other attributes)
9. `class`            — confidence: 0.05 (lowest; avoid unless no alternative)
10. `xpath`           — confidence: 0.05 (use only when no attribute selector works)
11. `css`             — confidence: 0.05 (use only when no attribute selector works)

In ZeuZ row blocks, use the selector type as col1 and selector value as col3:
```json
{"data": ["data-testid", "element parameter", "<selector-value>"], "sequence": 1}
```

---

## ZeuZ Element Anchoring — Combination Strategies

ZeuZ is NOT limited to single-attribute selectors. It supports powerful combination
strategies that make element location robust even without `data-automation` or `data-testid`.

### Parameter Types

| col2 value | Purpose | When to use |
|------------|---------|-------------|
| `element parameter` | Primary element locator | Default — locates the target element. Searches entire page. |
| `unique parameter`  | Fast single-match locator | When you know only ONE element matches. Faster (stops at first match). Cannot combine with parent/sibling/child/index. |
| `parent parameter`  | Parent element locator | When two elements have identical attributes but different parents. |
| `sibling parameter` | Sibling element locator | When elements AND their parents are identical but siblings differ. |
| `child parameter`   | Child element locator | Narrow search to children of a parent element. |

### Combining Multiple Attributes (AND Logic)

You can stack multiple `element parameter` rows to narrow down to a unique element.
ZeuZ uses AND logic — all attributes must match:

```json
{
  "rows": [
    {"data": ["tag",   "element parameter", "button"],  "sequence": 1},
    {"data": ["class", "element parameter", "btn-primary"], "sequence": 2},
    {"data": ["text",  "element parameter", "Submit"],  "sequence": 3},
    {"data": ["click", "selenium action",   "click"],   "sequence": 4}
  ]
}
```
This finds: a `<button>` with class `btn-primary` whose visible text is "Submit".

### Parent + Element (Parent-Child Selection)

When two elements have identical attributes but sit under different parents,
add a `parent parameter` row to disambiguate:

```json
{
  "rows": [
    {"data": ["id",    "parent parameter",  "login-form"],     "sequence": 1},
    {"data": ["class", "element parameter", "submit-btn"],     "sequence": 2},
    {"data": ["click", "selenium action",   "click"],          "sequence": 3}
  ]
}
```
This finds: `.submit-btn` that is a descendant of `#login-form`.

### Sibling Selection

When elements AND parents are identical, use a `sibling parameter` to disambiguate
via a nearby sibling element:

```json
{
  "rows": [
    {"data": ["text",  "sibling parameter", "Username"],       "sequence": 1},
    {"data": ["tag",   "element parameter",  "input"],         "sequence": 2},
    {"data": ["enter text", "selenium action", "enter text"],  "sequence": 3}
  ]
}
```
This finds: the `<input>` element that is a sibling of the element containing text "Username".

### Index Selection

When multiple elements match and you want a specific occurrence (0-based):

```json
{
  "rows": [
    {"data": ["class", "element parameter", "list-item"],      "sequence": 1},
    {"data": ["index", "element parameter", "0"],              "sequence": 2},
    {"data": ["click", "selenium action",   "click"],          "sequence": 3}
  ]
}
```
This clicks the FIRST element with class `list-item`.

### Partial Match — Single Asterisk (`*`)

Prefix the attribute name with `*` to match a PARTIAL value. Useful when part
of an attribute is dynamic (e.g. `id="user-card-12345"`):

```json
{
  "rows": [
    {"data": ["*id",   "element parameter", "user-card-"],     "sequence": 1},
    {"data": ["click", "selenium action",   "click"],          "sequence": 2}
  ]
}
```
This matches any element whose `id` CONTAINS "user-card-".

Works with ANY attribute: `*class`, `*text`, `*name`, `*data-testid`, etc.

### Case-Insensitive Partial Match — Double Asterisk (`**`)

Prefix with `**` for case-insensitive partial matching:

```json
{
  "rows": [
    {"data": ["**text", "element parameter", "sign in"],       "sequence": 1},
    {"data": ["click",  "selenium action",   "click"],         "sequence": 2}
  ]
}
```
This matches elements with text "Sign In", "SIGN IN", "sign in", etc.

### Allow Hidden Elements

Add an `optional option` row to interact with hidden/invisible elements:

```json
{
  "rows": [
    {"data": ["id",           "element parameter", "hidden-menu"],  "sequence": 1},
    {"data": ["allow hidden", "optional option",   "yes"],          "sequence": 2},
    {"data": ["click",        "selenium action",   "click"],        "sequence": 3}
  ]
}
```

### XPath and CSS Selectors (Last Resort)

Use these only when attribute combinations above cannot uniquely identify the element:

```json
{
  "rows": [
    {"data": ["xpath", "element parameter", "//div[@role='dialog']//button[last()]"], "sequence": 1},
    {"data": ["click", "selenium action",   "click"], "sequence": 2}
  ]
}
```

```json
{
  "rows": [
    {"data": ["css", "element parameter", "div.modal > footer > button.confirm"], "sequence": 1},
    {"data": ["click", "selenium action", "click"], "sequence": 2}
  ]
}
```

### Shadow DOM Elements

For shadow root traversal, prefix parameter types with `sr`:

```json
{
  "rows": [
    {"data": ["css", "sr element parameter", "#shadow-host"],      "sequence": 1},
    {"data": ["css", "element parameter",    ".inner-button"],     "sequence": 2},
    {"data": ["click", "selenium action",    "click"],             "sequence": 3}
  ]
}
```
Note: Shadow DOM only supports `element parameter` and `parent parameter` (no sibling/child/text).

### Mobile Selectors (Appium)

| Platform | Primary Selector | Fallback |
|----------|-----------------|----------|
| React Native | `testID` (capital D) | `accessibilityLabel` |
| Native Android | `resource-id` | `text`, `class` |
| Native iOS | `label` | `name`, `value` |

### Android-iOS Separator (`|*|`)

For cross-platform tests, use `|*|` to provide both selectors in one row:

```json
{"data": ["resource-id|*|label", "element parameter", "login_btn|*|Login Button"], "sequence": 1}
```

---

### Decision Tree — How to Choose the Right Anchoring Strategy

```
1. Does the element have data-automation, data-testid, or id?
   → YES: Use single attribute as element parameter. Done.
   → NO: Continue.

2. Can you combine 2-3 attributes (tag + class + text) to get a unique match?
   → YES: Stack multiple element parameter rows. Done.
   → NO: Continue.

3. Is there a unique parent container you can anchor to?
   → YES: Add parent parameter + element parameter. Done.
   → NO: Continue.

4. Is there a unique sibling near the target?
   → YES: Add sibling parameter + element parameter. Done.
   → NO: Continue.

5. Are there multiple matches and you need a specific one?
   → YES: Add index element parameter row. Done.
   → NO: Continue.

6. Can partial match (*) or case-insensitive match (**) narrow it down?
   → YES: Use * or ** prefix on the attribute name. Done.
   → NO: Use xpath or css as last resort. Mark confidence LOW.
```


---

## Forbidden Guessing Rules

1. **Never invent selector values.** Use ONLY values discovered in the evidence pack.
   If no selector is found for an element → write `"UNKNOWN"` as the value.

2. **Never invent endpoint URLs.** Use ONLY resolved_path values from rest_endpoints
   or graphql_operations in the evidence pack.
   If no URL is found → write `"UNKNOWN"` as the value.

3. **Never hardcode test logic.** Every step must be derivable from:
   - The action reference (row patterns)
   - The evidence pack (selectors, endpoints, examples)
   - The user's stated objective and flow steps

4. **Never invent data values.** Use variable references `%|var_name|%` for dynamic
   data. Use literal values only when they appear in the evidence.

5. **Mark unknowns explicitly.** If any part of a row cannot be determined from evidence,
   use `"UNKNOWN"` as the value. Do NOT make up a plausible-sounding value.

6. **Action identity rule.** Every action block MUST end with a valid action row whose:
   - col1 = action_name (from action reference)
   - col2 = zeuz_action_label (from action reference)
   - col3 = action_name again
   Example: `["click", "selenium action", "click"]`


---

## ZeuZ tc.json Output Rules

### Required Output Structure
Your output MUST be a single valid JSON object matching the tc.json schema above.
No markdown, no explanation, no surrounding text — ONLY the JSON object.

### Step Naming
- Use descriptive step names: "Login to Application", "Navigate to Dashboard", "Verify Login Success"
- description and expected fields accept HTML: wrap in `<p>...</p>`

### Variable References
ZeuZ uses `%|variable_name|%` syntax for dynamic values:
- `%|username|%`   — injected username
- `%|password|%`   — injected password
- `%|token|%`      — value saved from a previous step
- `%|base_url|%`   — base URL (if configured)
See the Variable Syntax Reference section for full dot-notation, array indexing, and function syntax.

- `%|RunTimeIP|%`  — runtime machine IP

#### Variable Access Patterns
- Basic: `%|variable_name|%`
- Dict key: `%|variable['key']|%` or `%|variable["key"]|%`
- List index: `%|variable[0]|%` (zero-indexed), `%|variable[-1]|%` (last)
- Nested: `%|response["data"]["users"][0]["name"]|%`

#### Shared Variables API (in execute python code)
- Set: `sr.Set_Shared_Variables("key", value)`
- Get: `sr.Get_Shared_Variables("key")`
- Test: `sr.Test_Shared_Variables("key")` (returns True if exists)

### Sequence Numbers
- Steps: sequence starting at 1, incrementing by 1
- Actions within a step: sequence starting at 1, incrementing by 1
- Rows within an action: sequence starting at 1, incrementing by 1
- IDs: use incrementing integers starting at 1

### Time Fields
- step `time`: integer (seconds), estimate per step (e.g., 30)
- testCaseDetail `time`: "HH:MM:SS" string (e.g., "00:05:00")

### verifyPoint and continuePoint

`verifyPoint` and `continuePoint` are **step-level flags** (set on the step, not the action):

| Flag            | Default | When to set `true`                                                              |
|-----------------|---------|---------------------------------------------------------------------------------|
| `verifyPoint`   | false   | Step is a **hard assertion** — if it fails, the test STOPS immediately. Use for critical assertions (login success, payment confirmed). |
| `continuePoint` | false   | Step should **continue even if earlier steps failed**. Use as a recovery point — e.g., "navigate back to home regardless of previous failures". |

**Rules:**
- Set `verifyPoint: true` on ALL assertion/verification steps that must pass for the test to be valid.
- Set `continuePoint: true` on cleanup or teardown steps that must always run.
- Both `verifyPoint` and `continuePoint` appear in TWO places per step: in the top-level step dict AND inside `stepInfo`.
- A step can have BOTH set to `true` (rare — means: assert AND continue if prior failed).

**Example — hard assertion step:**
```json
{
  "verifyPoint": true,
  "continuePoint": false,
  "stepInfo": {
    "verifyPoint": true,
    "stepContinue": false
  }
}
```

**Example — cleanup step (always runs):**
```json
{
  "verifyPoint": false,
  "continuePoint": true,
  "stepInfo": {
    "verifyPoint": false,
    "stepContinue": true
  }
}
```

### Common Step Patterns
1. **Init / Setup step**: Store variables, set base URL — `verifyPoint: false`
2. **Navigate step**: Go to URL — `verifyPoint: false`
3. **Action step**: Click, type, select, submit — `verifyPoint: false`
4. **Assert step**: Verify text, check element — `verifyPoint: true` ← ALWAYS
5. **API/GraphQL step**: REST call, save response — `verifyPoint: false`
6. **DB Validation step**: Execute query, compare result — `verifyPoint: true`
7. **Teardown step**: Close session, clean up — `continuePoint: true`


---

### Available Evidence Summary
- Pages/Screens: 0 found
- Selectors: 0 found
- REST Endpoints: 0 found
- GraphQL Operations: 0 found
- DB Queries: 0 found
- Similar Examples: 0 retrieved
- Assertion Anchors: 20 found
- Negative Cases: 0 found
- Auth Info: yes
- Schemas: 0 found

---



---

## Final Instructions

1. Read TEST_EVIDENCE_PACK.json for all selector values, endpoint URLs, and GraphQL documents.
2. Read `test_support.assertion_anchors` — use these as the basis for ALL verify/assert steps.
3. Read `test_support.negative_cases` — include at least one negative scenario if present.
4. Read `test_support.auth_info` — use login_endpoint and token_location for auth setup step.
5. Read `test_support.top_schemas` — use field names when building REST/SOAP/DB row values.
6. Apply ONLY the row patterns matching the detected surfaces above (irrelevant surfaces omitted).
7. Use the similar testcases above as structural templates only — do NOT copy their selector values.
8. Use variable chaining (`%|var|%`) to pass data between steps (auth token, IDs, response fields).
9. Set `verifyPoint: true` on every assertion/verification step; `continuePoint: true` on teardown.
10. For bulk data extraction, use `save attribute values in list` with `target parameter` rows.
11. For runtime-only / dynamic DOM scenarios where no selector works, use `classifier ai` as last resort.
12. Output ONLY valid JSON matching the tc.json schema. No markdown fences, no commentary.
13. If you cannot find evidence for a required value, write "UNKNOWN" — do NOT invent.

Generate the tc.json now.
