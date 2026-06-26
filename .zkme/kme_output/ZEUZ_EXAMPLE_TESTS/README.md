# ZeuZ Example Tests

> **For AI agents**: This folder contains real, working ZeuZ tc.json test cases.
> Study these examples to understand the correct structure, action patterns,
> selector usage, step naming conventions, and overall test composition
> BEFORE generating your own tests.

## Purpose

These are **production-grade test examples** — not templates or schemas.
They show exactly how real ZeuZ tests look, including:

- Complete tc.json structure with all required fields
- Real selector values and how they're used in action rows
- Step naming conventions and description/expected format
- Multi-step flows (login → navigate → action → verify)
- API test patterns (setup → call → validate response)
- Database verification patterns
- Variable usage (`%|var|%` syntax in real context)

## How to Use (for AI Agents)

**IMPORTANT**: Read these examples BEFORE generating any test.

1. **Read `INDEX.json`** — lists all available example tests with summaries
2. **Find similar examples** — match by feature type, surface, or test pattern
3. **Study the structure** — note how steps are named, how actions are sequenced,
   how selectors are referenced, and how variables flow between steps
4. **Learn the patterns** — observe which row patterns are used for each action type
5. **Apply to your test** — use the same structural patterns with selectors
   from `static/ui_surface_index.json`

### What to Learn from Each Example

| Look at... | To learn... |
|------------|-------------|
| `testCaseDetail` | Naming, priority, time format conventions |
| Step `name` and `description` | How to write clear, human-readable step descriptions |
| Step `expected` | How to phrase expected outcomes |
| Action `rows` | Exact row patterns (col1, col2, col3) for each action type |
| Sequence numbers | How step, action, and row sequences are numbered |
| Variable references | How `%|var|%` is used across steps |

## Folder Structure

```
ZEUZ_EXAMPLE_TESTS/
├── README.md          ← This file
├── INDEX.json         ← Master index of all example tests
├── ui/                ← Web UI test examples
├── api/               ← REST API test examples
├── mobile/            ← Mobile test examples
├── db/                ← Database test examples
├── e2e/               ← End-to-end flow test examples
└── mixed/             ← Multi-surface test examples (UI + API + DB)
```

## How to Add Example Tests

1. Export a real tc.json from ZeuZ (or create one manually)
2. Place it in the appropriate subfolder
3. Name it descriptively: `login_valid_credentials.json`, `create_user_api.json`
4. Run `zkme scan` — INDEX.json will be regenerated

## Gap Analysis

Compare example tests against `ZEUZ_GLOBAL_STEPS/INDEX.json`:
- **Examples without global steps** = opportunities to extract reusable steps
- **Global steps without examples** = steps that lack real-world validation

---

*Upload existing ZeuZ test cases here so AI can learn from real patterns.*
