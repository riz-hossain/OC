#!/usr/bin/env python
"""Export Playwright specs from ZKME portable testcases."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


RUNNER_DIR = Path(__file__).resolve().parent
REPO_ROOT = RUNNER_DIR.parents[2]
DEFAULT_TESTCASE_DIR = RUNNER_DIR / "test-cases"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "qa" / "automation" / "web" / "playwright" / "generated"


def _safe_name(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_]+", "_", value).strip("_").lower() or "portable_testcase"


def _js(value: Any) -> str:
    return json.dumps(value)


def _locator_expr(step: dict[str, Any]) -> str:
    pw = step.get("playwright", {}) if isinstance(step.get("playwright"), dict) else {}
    if pw.get("testId"):
        return f"page.getByTestId({_js(pw['testId'])})"
    locator = pw.get("locator") or step.get("selector")
    if not locator:
        return "page.locator('body')"
    return f"page.locator({_js(locator)})"


def _step_to_ts(step: dict[str, Any]) -> list[str]:
    pw = step.get("playwright", {}) if isinstance(step.get("playwright"), dict) else {}
    step_input = step.get("input", {}) if isinstance(step.get("input"), dict) else {}
    method = (pw.get("method") or step.get("action") or "").strip().lower()
    comment = f"  // {step.get('id', 'step')}: {step.get('intent', step.get('action', ''))}"
    locator = _locator_expr(step)
    if method in {"go to link", "goto", "navigate", "open"}:
        url = step_input.get("url") or step.get("url") or step.get("selector") or "/"
        return [comment, f"  await page.goto({_js(url)});"]
    if method == "click":
        return [comment, f"  await {locator}.click();"]
    if method == "double click":
        return [comment, f"  await {locator}.dblclick();"]
    if method == "right click":
        return [comment, f"  await {locator}.click({{ button: 'right' }});"]
    if method == "hover":
        return [comment, f"  await {locator}.hover();"]
    if method in {"text", "fill", "clear and enter text"}:
        value = step_input.get("value", step_input.get("text", ""))
        return [comment, f"  await {locator}.fill({_js(value)});"]
    if method in {"validate full text", "validate partial text", "assert text", "expect text"}:
        expected = step_input.get("expectedText") or step.get("expected") or ""
        assertion = "toHaveText" if method == "validate full text" else "toContainText"
        return [comment, f"  await expect({locator}).{assertion}({_js(expected)});"]
    if method in {"wait for element", "wait"}:
        return [comment, f"  await expect({locator}).toBeVisible();"]
    if method in {"take screenshot web", "screenshot"}:
        name = _safe_name(step.get("id", "screenshot")) + ".png"
        return [comment, f"  await page.screenshot({{ path: {_js(name)}, fullPage: true }});"]
    return [comment, f"  // TODO: unsupported Playwright action from portable testcase: {_js(method)}"]


def export_spec(testcase_path: Path, output_dir: Path = DEFAULT_OUTPUT_DIR) -> Path:
    testcase = json.loads(testcase_path.read_text(encoding="utf-8"))
    output_dir.mkdir(parents=True, exist_ok=True)
    test_id = testcase.get("id") or testcase_path.stem
    title = testcase.get("title") or test_id
    lines = [
        "import { test, expect } from '@playwright/test';",
        "",
        f"test({_js(title)}, async ({{ page }}) => {{",
        f"  // Source portable testcase: {testcase_path.as_posix()}",
    ]
    web_steps = [step for step in testcase.get("steps", []) if step.get("adapter") == "playwright"]
    if not web_steps:
        lines.append("  // No Playwright steps were present in this portable testcase.")
    for step in web_steps:
        lines.extend(_step_to_ts(step))
    lines.append("});")
    spec_path = output_dir / f"{_safe_name(test_id)}.spec.ts"
    spec_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return spec_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Export Playwright specs from ZKME portable testcase JSON.")
    parser.add_argument("paths", nargs="*", help="Portable testcase JSON files. Defaults to test-cases/*.json.")
    parser.add_argument("--out", default=str(DEFAULT_OUTPUT_DIR), help="Output directory for generated specs.")
    args = parser.parse_args()
    paths = [Path(path) for path in args.paths] if args.paths else sorted(DEFAULT_TESTCASE_DIR.glob("*.json"))
    if not paths:
        raise SystemExit(f"No portable testcase JSON files found under {DEFAULT_TESTCASE_DIR}")
    for path in paths:
        spec_path = export_spec(path, Path(args.out))
        print(f"Wrote Playwright spec: {spec_path}")


if __name__ == "__main__":
    main()
