#!/usr/bin/env python
"""Verify that a feature change has matching ZKME QA evidence.

This is a lightweight local/CI gate. It does not prove test quality by itself,
but it prevents feature work from silently skipping the QA evidence required by
qa/AI_TEST_GENERATION_CONTRACT.md.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
QA_ROOT = REPO_ROOT / "qa"


EXCLUDED_NAMES = {
    "README.md",
    "FEATURE_TEST_CASE.template.md",
    "FEATURE_UNIT_TEST.template.md",
    "FEATURE_E2E_TEST.template.md",
    "FEATURE_PLAYWRIGHT_TEST.template.md",
    "SAMPLE_PORTABLE_TESTCASE.json",
    "zeuz-report.schema.json",
    "zkme-portable-testcase.schema.json",
    "zeuz-export-manifest.json",
}


def _norm(path: str) -> str:
    return path.replace("\\", "/").lower()


def _is_evidence_file(path: Path) -> bool:
    if not path.is_file():
        return False
    if path.name in EXCLUDED_NAMES:
        return False
    if ".template." in path.name:
        return False
    if path.suffix.lower() in {".md", ".json", ".py", ".ts", ".tsx", ".js", ".jsx", ".feature", ".robot", ".yaml", ".yml"}:
        return True
    return False


def _evidence_under(*parts: str) -> list[str]:
    folder = QA_ROOT.joinpath(*parts)
    if not folder.exists():
        return []
    return sorted(str(path.relative_to(REPO_ROOT)).replace("\\", "/") for path in folder.rglob("*") if _is_evidence_file(path))


def _classify_changed_file(path: str) -> set[str]:
    value = _norm(path)
    surfaces: set[str] = set()
    if value.startswith(("docs/", "qa/", ".zkme/")):
        return surfaces
    if any(part in value for part in ("/components/", "/pages/", "/app/", "/screens/", "/routes/", "/views/", "frontend/", "web/")):
        surfaces.add("web")
    if value.endswith((".tsx", ".jsx", ".vue", ".svelte", ".css", ".scss")):
        surfaces.add("web")
    if any(part in value for part in ("/api/", "/routes/", "/controllers/", "/handlers/", "/endpoints/", "/services/")):
        surfaces.add("api")
    if any(part in value for part in ("/migrations/", "/models/", "/schema/", "/repositories/", "/dao/", "/db/")):
        surfaces.add("db")
    if value.endswith((".sql",)):
        surfaces.add("db")
    if any(part in value for part in ("android/", "ios/", "mobile/", "react-native/", "/screens/")):
        surfaces.add("mobile")
    if any(part in value for part in ("desktop/", "electron/", "winui/", "wpf/")):
        surfaces.add("desktop")
    if not surfaces and value.endswith((".py", ".ts", ".tsx", ".js", ".jsx", ".java", ".cs", ".go", ".rb", ".php", ".rs")):
        surfaces.add("unit")
    return surfaces


def _inventory() -> dict[str, list[str]]:
    return {
        "manual": _evidence_under("manual", "test-cases"),
        "unit": _evidence_under("automation", "unit"),
        "api": _evidence_under("automation", "api") + _evidence_under("automation", "integration"),
        "web": _evidence_under("automation", "web", "playwright"),
        "e2e": _evidence_under("automation", "e2e"),
        "db": _evidence_under("automation", "db"),
        "mobile": _evidence_under("automation", "mobile"),
        "desktop": _evidence_under("automation", "desktop"),
        "portable": _evidence_under("automation", "local-runner", "test-cases") + _evidence_under("automation", "testcases"),
        "zeuz": _evidence_under("automation", "zeuz", "test-cases") + _evidence_under("automation", "zeuz", "global-steps") + _evidence_under("automation", "testcases"),
    }


def verify(changed_files: list[str], require_feature_evidence: bool) -> dict[str, Any]:
    evidence = _inventory()
    surfaces: set[str] = set()
    for changed_file in changed_files:
        surfaces.update(_classify_changed_file(changed_file))

    required: dict[str, str] = {}
    if require_feature_evidence or surfaces:
        required["manual"] = "Every feature change needs a manual acceptance case."
    if require_feature_evidence:
        required["unit"] = "Feature changes need unit evidence or an explicit not-applicable file."
    if "unit" in surfaces:
        required["unit"] = "Source changes need unit evidence or an explicit not-applicable file."
    if "api" in surfaces:
        required["api"] = "API/service changes need API or integration evidence."
    if "web" in surfaces:
        required["web"] = "Web UI changes need Playwright evidence or an E2E candidate."
    if "db" in surfaces:
        required["db"] = "Database changes need DB or integration evidence."
    if "mobile" in surfaces:
        required["mobile"] = "Mobile changes need mobile evidence or an explicit candidate."
    if "desktop" in surfaces:
        required["desktop"] = "Desktop changes need desktop evidence or an explicit candidate."

    cross_surface = len(surfaces.intersection({"web", "api", "db", "mobile", "desktop"})) >= 2
    if cross_surface:
        required["portable"] = "Cross-surface changes need a portable or ZeuZ-compatible testcase."

    failures = []
    for key, message in required.items():
        if evidence.get(key):
            continue
        if key in {"api", "db"} and evidence.get("portable"):
            continue
        if key in {"web", "mobile", "desktop"} and (evidence.get("portable") or evidence.get("e2e")):
            continue
        failures.append({"target": key, "message": message})

    return {
        "schemaVersion": "zkme.qa-contract-verification.v1",
        "status": "passed" if not failures else "failed",
        "changedFiles": changed_files,
        "detectedSurfaces": sorted(surfaces),
        "requiredEvidence": sorted(required),
        "evidence": evidence,
        "failures": failures,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify ZKME QA evidence for a feature change.")
    parser.add_argument("--changed-file", action="append", default=[], help="Changed repo-relative file path. Repeat for multiple files.")
    parser.add_argument("--changed-files-from", help="Text file containing one changed repo-relative path per line.")
    parser.add_argument("--require-feature-evidence", action="store_true", help="Require manual and unit evidence even when no changed files are provided.")
    parser.add_argument("--json", action="store_true", help="Print JSON only.")
    args = parser.parse_args()

    changed_files = list(args.changed_file)
    if args.changed_files_from:
        source = Path(args.changed_files_from)
        changed_files.extend(line.strip() for line in source.read_text(encoding="utf-8").splitlines() if line.strip())

    result = verify(changed_files, args.require_feature_evidence)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"ZKME QA contract verification: {result['status']}")
        if result["detectedSurfaces"]:
            print("Detected surfaces: " + ", ".join(result["detectedSurfaces"]))
        if result["requiredEvidence"]:
            print("Required evidence: " + ", ".join(result["requiredEvidence"]))
        for failure in result["failures"]:
            print(f"FAIL [{failure['target']}]: {failure['message']}")
    raise SystemExit(0 if result["status"] == "passed" else 1)


if __name__ == "__main__":
    main()
