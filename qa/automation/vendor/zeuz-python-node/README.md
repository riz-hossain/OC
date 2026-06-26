# ZeuZ Node Runtime

This folder is for optionally vendoring the open-source ZeuZ Node runtime into this repo.

Default ZKME mode is thin bridge mode: portable testcases plus lightweight adapters. Use the full runtime only when local execution needs ZeuZ Node's existing platform functions directly.

## Official Source

- Repository: `https://github.com/AutomationSolutionz/Zeuz_Python_Node`
- Dev zip: `https://github.com/AutomationSolutionz/Zeuz_Python_Node/archive/refs/heads/dev.zip`

## Install Runtime

Copy from a local sibling checkout when available:

```bash
python qa/automation/vendor/zeuz-python-node/fetch_zeuz_node.py --source A:/git/Zeuz_Python_Node
```

Download the official open-source dev zip:

```bash
python qa/automation/vendor/zeuz-python-node/fetch_zeuz_node.py
```

The runtime is installed under:

```text
qa/automation/vendor/zeuz-python-node/runtime/
```

## Rule For AI Agents

Use this runtime only through thin adapters under `qa/automation/local-runner/adapters/`. Keep portable testcase JSON as the source of truth and keep local reports compatible with `zkme.zeuz-compatible-report.v1`.
