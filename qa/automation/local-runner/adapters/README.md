# Local Runner Adapters

This folder is for thin adapters that execute portable ZKME testcases in the target repo.

## Required Shape

- `zeuz_bridge/`: shared bridge for ZeuZ-derived action rows, variables, status mapping, and report projection
- `python/`: Python-native runner helpers, direct ZeuZ Node import/subprocess wrappers, pytest helpers
- `typescript/`: Playwright/Node helpers that read portable testcase JSON
- `java/`: JVM runner helpers that read portable testcase JSON
- `csharp/`: .NET runner helpers that read portable testcase JSON

## ZeuZ Function Reuse

Read these first when present:

- `.zkme/kme_output/ZEUZ_FUNCTION_CATALOG.md`
- `.zkme/kme_output/static/zeuz_function_catalog.v1.json`
- `.zkme/kme_output/AUTOMATION_SOLUTIONZ_ZEUZ_KIT.md`

ZKME should reuse ZeuZ capabilities through a bridge, not by copying the entire ZeuZ Node runtime into this repo.

When a full runtime is required, install it with:

```bash
python qa/automation/vendor/zeuz-python-node/fetch_zeuz_node.py
```

## Language Rule

Use the repo's native language and test runner when it is already established. Keep the portable testcase JSON and ZeuZ-compatible report format consistent across languages.

For non-Python suites, call the Python ZeuZ bridge through a local CLI/subprocess until a native wrapper exists for that language.
