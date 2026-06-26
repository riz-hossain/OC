#!/usr/bin/env python
"""Validate that common AI coding tools can see ZKME rules."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]

REQUIRED_TOKENS = [
    "ZKME",
    "QA_AUTOMATION_STANDARDS",
    "UI_UX_STANDARDS",
    "AI_TEST_GENERATION_CONTRACT",
]

ADAPTERS = [
    {"name": "codex", "paths": ["AGENTS.md", ".zkme/generated-governance/AGENTS.generated.md"]},
    {"name": "claude", "paths": ["CLAUDE.md"]},
    {"name": "cursor", "paths": [".cursor/rules/zkme.mdc"]},
    {"name": "copilot", "paths": [".github/copilot-instructions.md"]},
    {"name": "cline", "paths": [".clinerules"]},
    {"name": "roo", "paths": [".roo/rules/zkme.md"]},
    {"name": "windsurf", "paths": [".windsurfrules"]},
    {"name": "aider", "paths": [".aider.conf.yml"]},
]

ENFORCEMENT_FILES = [
    ".githooks/pre-commit",
    ".github/pull_request_template.md",
    ".github/workflows/zkme-qa.yml",
    "qa/automation/verify_zkme_qa_contract.py",
    "qa/automation/validate_testcase_packages.py",
    "qa/automation/validate_test_design_quality.py",
]


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def _adapter_status(adapter: dict[str, Any]) -> dict[str, Any]:
    candidates = [REPO_ROOT / raw for raw in adapter["paths"]]
    existing = [path for path in candidates if path.exists()]
    if not existing:
        return {
            "name": adapter["name"],
            "status": "failed",
            "paths": adapter["paths"],
            "message": "No adapter instruction file found.",
        }
    token_hits = {token: False for token in REQUIRED_TOKENS}
    for path in existing:
        text = _read(path)
        for token in REQUIRED_TOKENS:
            if token in text:
                token_hits[token] = True
    missing = [token for token, found in token_hits.items() if not found]
    return {
        "name": adapter["name"],
        "status": "passed" if not missing else "failed",
        "paths": [str(path.relative_to(REPO_ROOT)).replace("\\", "/") for path in existing],
        "missingTokens": missing,
        "message": "OK" if not missing else "Adapter file exists but does not reference all required ZKME rules.",
    }


def verify() -> dict[str, Any]:
    adapters = [_adapter_status(adapter) for adapter in ADAPTERS]
    enforcement = []
    for raw in ENFORCEMENT_FILES:
        path = REPO_ROOT / raw
        enforcement.append({"path": raw, "exists": path.exists()})
    failures = [
        {"target": item["name"], "message": item["message"], "missingTokens": item.get("missingTokens", [])}
        for item in adapters
        if item["status"] != "passed"
    ]
    failures.extend(
        {"target": item["path"], "message": "Required enforcement file is missing.", "missingTokens": []}
        for item in enforcement
        if not item["exists"]
    )
    return {
        "schemaVersion": "zkme.ai-adapter-validation.v1",
        "status": "passed" if not failures else "failed",
        "adapters": adapters,
        "enforcementFiles": enforcement,
        "failures": failures,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate ZKME AI adapter instruction files.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    args = parser.parse_args()
    result = verify()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"ZKME AI adapter validation: {result['status']}")
        for failure in result["failures"]:
            print(f"FAIL [{failure['target']}]: {failure['message']}")
    raise SystemExit(0 if result["status"] == "passed" else 1)


if __name__ == "__main__":
    main()
