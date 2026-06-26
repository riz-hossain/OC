#!/usr/bin/env python
"""Scan UI component inventory and gate duplicate primitive systems."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[2]
UI_ROOT = SCRIPT_DIR
INVENTORY_PATH = UI_ROOT / "component-inventory.json"
REPORT_PATH = UI_ROOT / "ui-consistency-report.json"
EXCEPTIONS_PATH = UI_ROOT / "ui-exceptions.json"

SOURCE_EXTENSIONS = {".tsx", ".jsx", ".vue", ".svelte", ".ts", ".js"}
STYLE_EXTENSIONS = {".css", ".scss", ".sass", ".less"}
SKIP_PARTS = {".git", ".zkme", "qa", "node_modules", "dist", "build", "coverage", ".next", ".nuxt", "vendor"}
PRIMITIVES = {
    "button",
    "input",
    "card",
    "modal",
    "dialog",
    "select",
    "checkbox",
    "radio",
    "table",
    "toast",
    "dropdown",
}
COMPONENT_LIBRARY_PACKAGES = {
    "@mui/material": "mui",
    "@chakra-ui/react": "chakra",
    "antd": "ant-design",
    "@mantine/core": "mantine",
    "@radix-ui/react-dialog": "radix",
    "@radix-ui/react-popover": "radix",
    "@headlessui/react": "headless-ui",
    "react-bootstrap": "bootstrap",
    "bootstrap": "bootstrap",
    "semantic-ui-react": "semantic-ui",
    "primereact": "primereact",
    "shadcn-ui": "shadcn",
    "tailwindcss": "tailwind",
}


def _rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT.resolve())).replace("\\", "/")
    except Exception:
        return str(path).replace("\\", "/")


def _iter_files() -> list[Path]:
    files: list[Path] = []
    for path in REPO_ROOT.rglob("*"):
        if any(part in SKIP_PARTS for part in path.parts):
            continue
        if path.is_file() and path.suffix.lower() in SOURCE_EXTENSIONS.union(STYLE_EXTENSIONS, {".json"}):
            files.append(path)
    return files


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _package_jsons() -> list[dict[str, Any]]:
    packages = []
    for path in REPO_ROOT.rglob("package.json"):
        if any(part in SKIP_PARTS for part in path.parts):
            continue
        payload = _load_json(path)
        if isinstance(payload, dict):
            payload["_path"] = _rel(path)
            packages.append(payload)
    return packages


def detect_component_libraries() -> list[dict[str, str]]:
    libraries: dict[str, dict[str, str]] = {}
    for package in _package_jsons():
        deps = {}
        for key in ("dependencies", "devDependencies", "peerDependencies"):
            if isinstance(package.get(key), dict):
                deps.update(package[key])
        for dep_name, version in deps.items():
            library = COMPONENT_LIBRARY_PACKAGES.get(dep_name)
            if library:
                libraries[library] = {"name": library, "package": dep_name, "version": str(version), "source": str(package.get("_path", ""))}
    return sorted(libraries.values(), key=lambda item: item["name"])


def detect_design_tokens(files: list[Path]) -> list[dict[str, str]]:
    tokens: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    token_file_patterns = ("token", "theme", "tailwind.config", "design-system")
    css_var_re = re.compile(r"--([a-zA-Z0-9_-]+)\s*:")
    for path in files:
        rel = _rel(path)
        lowered = rel.lower()
        if any(pattern in lowered for pattern in token_file_patterns):
            key = ("file", rel)
            if key not in seen:
                tokens.append({"kind": "file", "name": path.name, "path": rel})
                seen.add(key)
        if path.suffix.lower() in STYLE_EXTENSIONS:
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            for match in css_var_re.finditer(text):
                key = ("css-var", match.group(1))
                if key not in seen:
                    tokens.append({"kind": "css-var", "name": "--" + match.group(1), "path": rel})
                    seen.add(key)
    return tokens[:300]


def _component_names_from_text(text: str) -> list[str]:
    names: list[str] = []
    patterns = [
        re.compile(r"(?:export\s+default\s+)?(?:function|class)\s+([A-Z][A-Za-z0-9_]*)"),
        re.compile(r"(?:export\s+)?const\s+([A-Z][A-Za-z0-9_]*)\s*="),
        re.compile(r"defineComponent\s*\(\s*\{\s*name\s*:\s*['\"]([A-Z][A-Za-z0-9_]*)['\"]", re.MULTILINE),
    ]
    for pattern in patterns:
        names.extend(match.group(1) for match in pattern.finditer(text))
    return sorted(set(names))


def _primitive_for_name(name: str) -> str:
    lowered = name.lower()
    stem = re.sub(r"[^a-z0-9]+", "", lowered)
    return stem if stem in PRIMITIVES else ""


def detect_components(files: list[Path]) -> list[dict[str, str]]:
    components: list[dict[str, str]] = []
    for path in files:
        if path.suffix.lower() not in SOURCE_EXTENSIONS:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        names = _component_names_from_text(text)
        if path.suffix.lower() in {".vue", ".svelte"} and not names:
            names = [path.stem] if path.stem[:1].isupper() else []
        for name in names:
            primitive = _primitive_for_name(name)
            components.append({"name": name, "primitive": primitive, "path": _rel(path)})
    return sorted(components, key=lambda item: (item["primitive"], item["name"], item["path"]))


def load_exceptions() -> dict[str, Any]:
    payload = _load_json(EXCEPTIONS_PATH)
    return payload if isinstance(payload, dict) else {"allowedDuplicatePrimitives": []}


def allowed_duplicate(exception_payload: dict[str, Any], primitive: str, paths: list[str]) -> bool:
    for item in exception_payload.get("allowedDuplicatePrimitives", []):
        if not isinstance(item, dict):
            continue
        if str(item.get("primitive", "")).lower() != primitive:
            continue
        allowed_paths = {str(path).replace("\\", "/") for path in item.get("paths", [])}
        if set(paths).issubset(allowed_paths):
            return True
    return False


def duplicate_primitive_findings(components: list[dict[str, str]], exceptions: dict[str, Any]) -> list[dict[str, Any]]:
    by_primitive: dict[str, list[dict[str, str]]] = {}
    for component in components:
        primitive = component.get("primitive", "")
        if primitive:
            by_primitive.setdefault(primitive, []).append(component)
    findings = []
    for primitive, items in sorted(by_primitive.items()):
        paths = sorted({item["path"] for item in items})
        names = sorted({item["name"] for item in items})
        if len(paths) <= 1:
            continue
        if allowed_duplicate(exceptions, primitive, paths):
            continue
        findings.append(
            {
                "primitive": primitive,
                "names": names,
                "paths": paths,
                "message": f"Duplicate {primitive} primitive implementations detected. Reuse one system or document an exception.",
            }
        )
    return findings


def _changed_files(path: str | None) -> list[str]:
    if not path:
        return []
    source = Path(path)
    if not source.is_absolute():
        source = REPO_ROOT / source
    if not source.exists():
        return []
    return [line.strip().replace("\\", "/") for line in source.read_text(encoding="utf-8").splitlines() if line.strip()]


def _ui_changed(changed_files: list[str]) -> bool:
    if not changed_files:
        return True
    for path in changed_files:
        lowered = path.lower()
        suffix = Path(path).suffix.lower()
        if suffix in SOURCE_EXTENSIONS.union(STYLE_EXTENSIONS):
            if any(part in lowered for part in ("component", "page", "screen", "view", "ui", "frontend", "web", "app/")):
                return True
    return False


def scan(changed_files_from: str | None = None) -> dict[str, Any]:
    files = _iter_files()
    components = detect_components(files)
    libraries = detect_component_libraries()
    tokens = detect_design_tokens(files)
    exceptions = load_exceptions()
    duplicates = duplicate_primitive_findings(components, exceptions)
    changed_files = _changed_files(changed_files_from)
    should_gate = _ui_changed(changed_files)
    failures = duplicates if should_gate else []
    return {
        "schemaVersion": "zkme.ui-consistency.v1",
        "status": "passed" if not failures else "failed",
        "changedFiles": changed_files,
        "uiChangeDetected": should_gate,
        "componentLibraries": libraries,
        "designTokens": tokens,
        "components": components,
        "duplicatePrimitiveFindings": duplicates,
        "requiredVisualAccessibilityChecks": [
            "default/hover/active/focus/disabled/loading states",
            "empty/error/denied/partial/success data states",
            "mobile/tablet/desktop responsive layouts",
            "keyboard order and focus visibility",
            "accessible names, roles, and form error associations",
        ],
        "failures": failures,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify ZKME UI consistency rules.")
    parser.add_argument("--changed-files-from", help="Text file containing changed repo-relative paths.")
    parser.add_argument("--write-inventory", action="store_true", help="Write qa/automation/ui/component-inventory.json.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    args = parser.parse_args()

    result = scan(args.changed_files_from)
    if args.write_inventory:
        INVENTORY_PATH.write_text(json.dumps({
            "schemaVersion": "zkme.ui-component-inventory.v1",
            "componentLibraries": result["componentLibraries"],
            "designTokens": result["designTokens"],
            "components": result["components"],
        }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"ZKME UI consistency: {result['status']}")
        print(f"Components: {len(result['components'])}; libraries: {len(result['componentLibraries'])}; design tokens: {len(result['designTokens'])}")
        for failure in result["failures"]:
            print(f"FAIL [{failure['primitive']}]: {failure['message']}")
    raise SystemExit(0 if result["status"] == "passed" else 1)


if __name__ == "__main__":
    main()
