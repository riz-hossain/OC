#!/usr/bin/env python
"""Validate ZKME canonical testcase packages."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
PACKAGE_ROOT = REPO_ROOT / "qa" / "automation" / "testcases"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT.resolve())).replace("\\", "/")
    except Exception:
        return str(path).replace("\\", "/")


def _resolve(base: Path, raw: str) -> Path:
    path = Path(raw)
    return path if path.is_absolute() else base / path


def _steps(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return [step for step in payload.get("steps", []) or [] if isinstance(step, dict)]


def _step_keys(payload: dict[str, Any]) -> list[str]:
    ids = []
    for index, step in enumerate(payload.get("steps", []) or [], start=1):
        if isinstance(step, dict):
            ids.append(str(step.get("stepKey") or step.get("id") or f"step-{index}"))
    return ids


def _zeuz_step_name(step: dict[str, Any], index: int) -> str:
    mapping = step.get("zeuzMapping") if isinstance(step.get("zeuzMapping"), dict) else {}
    zeuz = step.get("zeuz") if isinstance(step.get("zeuz"), dict) else {}
    return str(
        step.get("stepName")
        or step.get("name")
        or mapping.get("stepName")
        or zeuz.get("stepName")
        or step.get("intent")
        or step.get("action")
        or f"Step {index}"
    ).strip()


def _zeuz_step_names(payload: dict[str, Any]) -> list[str]:
    return [_zeuz_step_name(step, index) for index, step in enumerate(_steps(payload), start=1)]


def _duplicate_values(values: list[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for value in values:
        normalized = value.strip()
        if not normalized:
            continue
        if normalized in seen and normalized not in duplicates:
            duplicates.append(normalized)
        seen.add(normalized)
    return duplicates


def _binding_steps(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    steps = payload.get("steps")
    if isinstance(steps, dict):
        return {str(key): value for key, value in steps.items() if isinstance(value, dict)}
    if isinstance(steps, list):
        result: dict[str, dict[str, Any]] = {}
        for index, step in enumerate(steps, start=1):
            if isinstance(step, dict):
                key = str(step.get("stepKey") or step.get("id") or f"step-{index}")
                result[key] = step
        return result
    return {}


def discover_manifests(raw_paths: list[str]) -> list[Path]:
    if not raw_paths:
        return sorted(PACKAGE_ROOT.glob("**/manifest.json"))
    manifests: list[Path] = []
    for raw in raw_paths:
        path = Path(raw)
        if not path.is_absolute():
            path = REPO_ROOT / path
        if path.is_dir():
            manifests.extend(sorted(path.glob("**/manifest.json")))
        else:
            manifests.append(path)
    return manifests


def validate_manifest(path: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    package_dir = path.parent
    try:
        manifest = load_json(path)
    except Exception as exc:
        return [f"{rel(path)}: invalid JSON: {exc}"], warnings
    if manifest.get("schemaVersion") != "zkme.test-package.v1":
        errors.append(f"{rel(path)}: schemaVersion must be zkme.test-package.v1")
    testcase_id = str(manifest.get("testcaseId") or "")
    if not testcase_id:
        errors.append(f"{rel(path)}: missing testcaseId")
    logical_ref = (manifest.get("sourceOfTruth") or {}).get("logicalTestcase")
    if not logical_ref:
        errors.append(f"{rel(path)}: missing sourceOfTruth.logicalTestcase")
        return errors, warnings
    logical_path = _resolve(package_dir, str(logical_ref))
    if not logical_path.exists():
        errors.append(f"{rel(path)}: missing logical testcase {logical_ref}")
        return errors, warnings
    logical = load_json(logical_path)
    if logical.get("schemaVersion") != "zkme.logical-testcase.v1":
        errors.append(f"{rel(logical_path)}: schemaVersion must be zkme.logical-testcase.v1")
    if logical.get("id") != testcase_id:
        errors.append(f"{rel(logical_path)}: logical id does not match manifest testcaseId")
    logical_steps = _step_keys(logical)
    duplicate_logical_keys = _duplicate_values(logical_steps)
    if duplicate_logical_keys:
        errors.append(f"{rel(logical_path)}: duplicate logical stepKey values: {', '.join(duplicate_logical_keys)}")
    duplicate_logical_names = _duplicate_values(_zeuz_step_names(logical))
    if duplicate_logical_names:
        errors.append(f"{rel(logical_path)}: duplicate ZeuZ stepName values: {', '.join(duplicate_logical_names)}")
    implementations = manifest.get("implementations") if isinstance(manifest.get("implementations"), dict) else {}
    for name, implementation in implementations.items():
        if not isinstance(implementation, dict):
            errors.append(f"{rel(path)}: implementation {name} must be an object")
            continue
        entry = implementation.get("entry")
        if not entry:
            errors.append(f"{rel(path)}: implementation {name} missing entry")
            continue
        entry_path = _resolve(package_dir, str(entry))
        if not entry_path.exists():
            errors.append(f"{rel(path)}: implementation {name} entry missing: {entry}")
            continue
        if name == "portable":
            portable = load_json(entry_path)
            if portable.get("schemaVersion") != "zkme.portable-testcase.v1":
                errors.append(f"{rel(entry_path)}: portable schemaVersion mismatch")
            if portable.get("id") != testcase_id:
                errors.append(f"{rel(entry_path)}: portable id does not match package testcaseId")
            if _step_keys(portable) != logical_steps:
                errors.append(f"{rel(entry_path)}: portable stepKeys do not match logical testcase stepKeys")
        if name == "zeuzActions":
            zeuz = load_json(entry_path)
            if zeuz.get("schemaVersion") != "zkme.zeuz-actions-implementation.v1":
                errors.append(f"{rel(entry_path)}: zeuzActions schemaVersion mismatch")
            if zeuz.get("testcaseId") != testcase_id:
                errors.append(f"{rel(entry_path)}: zeuzActions testcaseId does not match package testcaseId")
            if _step_keys(zeuz) != logical_steps:
                errors.append(f"{rel(entry_path)}: ZeuZ action stepKeys do not match logical testcase stepKeys")
            duplicate_zeuz_names = _duplicate_values(_zeuz_step_names(zeuz))
            if duplicate_zeuz_names:
                errors.append(f"{rel(entry_path)}: duplicate ZeuZ action step names: {', '.join(duplicate_zeuz_names)}")
    binding_ref = (manifest.get("sourceOfTruth") or {}).get("zeuzBindings") or (manifest.get("identityPolicy") or {}).get("bindingFile")
    if implementations.get("zeuzActions"):
        if not binding_ref:
            errors.append(f"{rel(path)}: ZeuZ package missing sourceOfTruth.zeuzBindings")
        else:
            binding_path = _resolve(package_dir, str(binding_ref))
            if not binding_path.exists():
                errors.append(f"{rel(path)}: missing ZeuZ binding file {binding_ref}")
            else:
                bindings = load_json(binding_path)
                if bindings.get("schemaVersion") != "zkme.zeuz-bindings.v1":
                    errors.append(f"{rel(binding_path)}: schemaVersion must be zkme.zeuz-bindings.v1")
                if bindings.get("testcaseId") != testcase_id:
                    errors.append(f"{rel(binding_path)}: bindings testcaseId does not match package testcaseId")
                binding_steps = _binding_steps(bindings)
                missing = [key for key in logical_steps if key not in binding_steps]
                if missing:
                    errors.append(f"{rel(binding_path)}: missing ZeuZ binding entries for stepKeys: {', '.join(missing)}")
                binding_names = [str(step.get("stepName") or step.get("zeuzStepName") or "") for step in binding_steps.values()]
                duplicate_binding_names = _duplicate_values(binding_names)
                if duplicate_binding_names:
                    errors.append(f"{rel(binding_path)}: duplicate ZeuZ binding step names: {', '.join(duplicate_binding_names)}")
    if not implementations.get("portable"):
        warnings.append(f"{rel(path)}: package has no portable implementation")
    if not implementations.get("zeuzActions"):
        warnings.append(f"{rel(path)}: package has no ZeuZ actions implementation")
    return errors, warnings


def validate(paths: list[str]) -> dict[str, Any]:
    manifests = discover_manifests(paths)
    errors: list[str] = []
    warnings: list[str] = []
    for manifest in manifests:
        manifest_errors, manifest_warnings = validate_manifest(manifest)
        errors.extend(manifest_errors)
        warnings.extend(manifest_warnings)
    return {
        "schemaVersion": "zkme.test-package-validation.v1",
        "status": "passed" if not errors else "failed",
        "packageRoot": rel(PACKAGE_ROOT),
        "manifests": [rel(path) for path in manifests],
        "counts": {
            "packages": len(manifests),
            "errors": len(errors),
            "warnings": len(warnings)
        },
        "errors": errors,
        "warnings": warnings,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate ZKME testcase package structure.")
    parser.add_argument("paths", nargs="*", help="Package directories or manifest paths. Defaults to qa/automation/testcases/**/manifest.json.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = validate(args.paths)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"ZKME testcase package validation: {result['status']}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
        for warning in result["warnings"]:
            print(f"WARN: {warning}")
    raise SystemExit(0 if result["status"] == "passed" else 1)


if __name__ == "__main__":
    main()
