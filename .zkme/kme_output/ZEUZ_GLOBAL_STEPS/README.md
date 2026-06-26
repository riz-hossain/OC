# ZeuZ Global Steps Library

> **For AI agents**: This folder contains reusable ZeuZ test step templates.
> When generating tc.json tests, check here FIRST for pre-built steps that
> match your test scenario. Use them directly or adapt them.

## What Are Global Steps?

Global steps are like shared functions for ZeuZ tests. Each step is a complete,
reusable test operation with:

- **Human-readable description** — what the step does in plain language
- **Expected outcome** — what success looks like (for manual testers too)
- **Complete ZeuZ action rows** — ready to paste into tc.json
- **Surface/platform tags** — so you know when to use each step

## How to Use (for AI Agents)

1. **Read `INDEX.json`** — lists all available global steps with summaries
2. **Find matching steps** — match by name, surface, or capability tags
3. **Read the step file** — get the full action rows
4. **Adapt selectors** — replace placeholder selectors with real values from
   `static/ui_surface_index.json` or other surface indexes
5. **Compose your test** — chain global steps together into a complete tc.json

### Example: Building a test from global steps

```
Your test objective: "Verify user can log in and view their profile"

1. Read INDEX.json → find "GS-LOGIN-001" (Login) and "GS-NAV-001" (Navigate)
2. Read gs_login_001.json → get complete login step actions
3. Read gs_navigate_001.json → get navigate step actions
4. Replace placeholder selectors with real selectors from ui_surface_index.json
5. Compose: Login step → Navigate to profile → Verify profile data
```

## Folder Structure

```
ZEUZ_GLOBAL_STEPS/
├── README.md              ← This file
├── INDEX.json             ← Master index of all global steps
├── _SCHEMA.json           ← JSON schema for step files (for validation)
├── ui/                    ← Web UI steps (selenium)
│   ├── gs_login_001.json
│   ├── gs_navigate_001.json
│   └── ...
├── api/                   ← REST API steps
│   ├── gs_rest_get_001.json
│   └── ...
├── mobile/                ← Mobile steps (appium)
│   └── ...
├── db/                    ← Database steps
│   └── ...
└── common/                ← Cross-cutting steps (setup, teardown, variables)
    ├── gs_setup_001.json
    └── ...
```

## Step File Schema

Each `.json` file follows this structure:

```json
{
  "step_id": "GS-LOGIN-001",
  "name": "Login with valid credentials",
  "description": "Navigate to login page, enter username and password, click login button.",
  "expected": "User is redirected to the dashboard. Welcome message is displayed.",
  "surfaces": ["ui"],
  "capability_tags": ["ui_click", "ui_input", "ui_assert"],
  "platform": "web",
  "pre_conditions": ["Application is accessible", "Valid test credentials exist"],
  "steps": [
    {
      "step_name": "Navigate to Login Page",
      "description": "Open the login URL in browser",
      "expected": "Login page loads with username and password fields visible",
      "actions": [
        {
          "action_name": "Go to login URL",
          "rows": [
            {"data": ["url", "element parameter", "%|base_url|%/login"], "sequence": 1},
            {"data": ["go to url", "selenium action", "go to url"], "sequence": 2}
          ]
        }
      ]
    },
    {
      "step_name": "Enter Credentials and Submit",
      "description": "Type username and password, then click the login button",
      "expected": "Form accepts input and submits",
      "actions": [
        {
          "action_name": "Enter username",
          "rows": [
            {"data": ["id", "element parameter", "username"], "sequence": 1},
            {"data": ["%|username|%", "optional parameter", "%|username|%"], "sequence": 2},
            {"data": ["enter text", "selenium action", "enter text"], "sequence": 3}
          ]
        },
        {
          "action_name": "Enter password",
          "rows": [
            {"data": ["id", "element parameter", "password"], "sequence": 1},
            {"data": ["%|password|%", "optional parameter", "%|password|%"], "sequence": 2},
            {"data": ["enter text", "selenium action", "enter text"], "sequence": 3}
          ]
        },
        {
          "action_name": "Click login button",
          "rows": [
            {"data": ["id", "element parameter", "btn-login"], "sequence": 1},
            {"data": ["click", "selenium action", "click"], "sequence": 2}
          ]
        }
      ]
    },
    {
      "step_name": "Verify Login Success",
      "description": "Check that dashboard heading or welcome message is visible",
      "expected": "Dashboard page is displayed with welcome message",
      "actions": [
        {
          "action_name": "Wait for page load",
          "rows": [
            {"data": ["5", "element parameter", "5"], "sequence": 1},
            {"data": ["sleep", "common action", "sleep"], "sequence": 2}
          ]
        },
        {
          "action_name": "Verify dashboard text",
          "rows": [
            {"data": ["id", "element parameter", "dashboard-heading"], "sequence": 1},
            {"data": ["Dashboard", "optional parameter", "Dashboard"], "sequence": 2},
            {"data": ["validate text", "selenium action", "validate text"], "sequence": 3}
          ]
        }
      ]
    }
  ],
  "variables_used": ["base_url", "username", "password"],
  "notes": "Replace selector values (id=username, id=password, etc.) with actual selectors from ui_surface_index.json."
}
```

## Key Fields

| Field | Required | Description |
|-------|----------|-------------|
| `step_id` | Yes | Unique ID (format: `GS-<CATEGORY>-NNN`) |
| `name` | Yes | Human-readable name |
| `description` | Yes | What this step does (plain language) |
| `expected` | Yes | What success looks like |
| `surfaces` | Yes | `["ui"]`, `["rest"]`, `["mobile"]`, `["db"]`, etc. |
| `capability_tags` | Yes | Capability tags for matching |
| `platform` | Yes | `"web"`, `"mobile"`, `"desktop"`, `"any"` |
| `pre_conditions` | No | What must be true before this step runs |
| `steps` | Yes | Array of sub-steps with actions |
| `variables_used` | No | Variables this step reads/writes |
| `notes` | No | Adaptation notes for AI |

## How to Add New Global Steps

1. Create a JSON file following the schema above
2. Place it in the appropriate subfolder (`ui/`, `api/`, `mobile/`, `db/`, `common/`)
3. Run `zkme scan` — the INDEX.json will be regenerated automatically

## Gap Analysis

Compare the global steps library against the `static/flow_graph.v1.json` to
identify user flows that don't have corresponding global steps. These gaps
represent opportunities to build more reusable steps.

---

*Generated by ZKME v1.0 schema*
