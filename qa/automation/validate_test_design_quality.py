#!/usr/bin/env python
"""Validate deterministic lead-QA test design quality.

This gate is intentionally stdlib-only. It validates the artifacts ZKME
generates without requiring an AI model, ZeuZ Server, Playwright, or Appium.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
QA_ROOT = REPO_ROOT / "qa"
QUALITY_PATH = QA_ROOT / "test-design-quality.json"
REQUIRED_MODEL_FILES = [
    (QA_ROOT / "feature-architecture-map.json", "zkme.lead-qa-feature-architecture.v1"),
    (QA_ROOT / "workflow-map.json", "zkme.lead-qa-workflow-map.v1"),
    (QA_ROOT / "test-oracles.json", "zkme.lead-qa-test-oracles.v1"),
    (QA_ROOT / "risk-matrix.json", "zkme.lead-qa-risk-matrix.v1"),
    (QA_ROOT / "test-data-matrix.json", "zkme.lead-qa-test-data-matrix.v1"),
    (QA_ROOT / "traceability-matrix.json", "zkme.lead-qa-traceability-matrix.v1"),
]


REQUIRED_MANUAL_SECTIONS = [
    "## Objective",
    "## Architecture Path",
    "## Preconditions",
    "## Test Data",
    "## Lead QA Scenario Steps",
    "## Required Oracles",
    "## Required Evidence",
    "## Unknowns To Resolve",
    "## Automation Mapping",
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT.resolve())).replace("\\", "/")
    except Exception:
        return str(path).replace("\\", "/")


def _resolve(raw: str) -> Path:
    path = Path(raw)
    return path if path.is_absolute() else REPO_ROOT / path


def _manual_case_errors(score: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    manual_path = _resolve(str(score.get("manualCase") or ""))
    if not manual_path.exists():
        return [f"{score.get('featureId', '<unknown>')}: missing lead-QA manual case {rel(manual_path)}"]
    content = manual_path.read_text(encoding="utf-8", errors="replace")
    for section in REQUIRED_MANUAL_SECTIONS:
        if section not in content:
            errors.append(f"{rel(manual_path)}: missing section {section}")
    lower = content.lower()
    required = {str(item).lower() for item in score.get("requiredEvidence", []) or []}
    keyword_requirements = {
        "api": ("api", "status", "schema", "response"),
        "db": ("db", "database", "row", "query"),
        "playwright-or-visual": ("ui", "screenshot", "accessibility", "responsive"),
        "mobile-appium-or-zeuz": ("mobile", "appium", "device", "session"),
        "desktop-adapter-or-manual": ("desktop", "window", "process", "file"),
        "auth-negative": ("auth", "role", "tenant", "denied"),
        "async": ("queue", "job", "retry", "eventual"),
        "audit-report-log": ("audit", "report", "log", "artifact"),
        "portable-testcase": ("portable", "testcase", "automation"),
    }
    for key, keywords in keyword_requirements.items():
        if key in required and not any(keyword in lower for keyword in keywords):
            errors.append(f"{rel(manual_path)}: required evidence `{key}` is not reflected in the manual case")
    return errors


def validate(require_model: bool = False) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    if not QUALITY_PATH.exists():
        message = f"{rel(QUALITY_PATH)} not found; run ZKME scan to generate deterministic lead-QA artifacts."
        if require_model:
            errors.append(message)
        else:
            warnings.append(message)
        return {
            "schemaVersion": "zkme.lead-qa-quality-validation.v1",
            "status": "failed" if errors else "passed",
            "qualityPath": rel(QUALITY_PATH),
            "counts": {"features": 0, "errors": len(errors), "warnings": len(warnings)},
            "errors": errors,
            "warnings": warnings,
        }
    try:
        model = load_json(QUALITY_PATH)
    except Exception as exc:
        return {
            "schemaVersion": "zkme.lead-qa-quality-validation.v1",
            "status": "failed",
            "qualityPath": rel(QUALITY_PATH),
            "counts": {"features": 0, "errors": 1, "warnings": 0},
            "errors": [f"{rel(QUALITY_PATH)}: invalid JSON: {exc}"],
            "warnings": [],
        }
    if model.get("schemaVersion") != "zkme.lead-qa-test-design-quality.v1":
        errors.append(f"{rel(QUALITY_PATH)}: schemaVersion must be zkme.lead-qa-test-design-quality.v1")
    for path, schema_version in REQUIRED_MODEL_FILES:
        if not path.exists():
            errors.append(f"{rel(path)}: missing deterministic lead-QA companion artifact")
            continue
        try:
            companion = load_json(path)
        except Exception as exc:
            errors.append(f"{rel(path)}: invalid JSON: {exc}")
            continue
        if companion.get("schemaVersion") != schema_version:
            errors.append(f"{rel(path)}: schemaVersion must be {schema_version}")
    scores = model.get("scores") if isinstance(model.get("scores"), list) else []
    for score in scores:
        if not isinstance(score, dict):
            errors.append(f"{rel(QUALITY_PATH)}: score entry must be an object")
            continue
        feature_id = score.get("featureId", "<unknown>")
        actual = int(score.get("score") or 0)
        threshold = int(score.get("threshold") or 0)
        if actual < threshold:
            errors.append(f"{feature_id}: lead-QA score {actual} is below threshold {threshold}")
        errors.extend(_manual_case_errors(score))
    return {
        "schemaVersion": "zkme.lead-qa-quality-validation.v1",
        "status": "passed" if not errors else "failed",
        "qualityPath": rel(QUALITY_PATH),
        "counts": {
            "features": len(scores),
            "errors": len(errors),
            "warnings": len(warnings),
        },
        "errors": errors,
        "warnings": warnings,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate ZKME lead-QA test design quality.")
    parser.add_argument("--require-model", action="store_true", help="Fail when qa/test-design-quality.json is missing.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = validate(require_model=args.require_model)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"ZKME lead-QA quality validation: {result['status']}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
        for warning in result["warnings"]:
            print(f"WARN: {warning}")
    raise SystemExit(0 if result["status"] == "passed" else 1)


if __name__ == "__main__":
    main()
