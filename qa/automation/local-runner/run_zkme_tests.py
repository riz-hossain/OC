#!/usr/bin/env python
"""Run ZKME portable testcases locally.

This runner is intentionally small and dependency-light. It can execute API,
SQLite DB, and manual/candidate steps with the Python standard library. Web
steps use Playwright when the optional `playwright` package is installed.
"""

from __future__ import annotations

import argparse
import json
import platform
import os
import shlex
import sqlite3
import subprocess
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from adapters.zeuz_bridge.report_writer import build_report, utc_now, write_report
from adapters.zeuz_bridge.status import aggregate_status
from adapters.zeuz_bridge.variables import Variables


RUNNER_DIR = Path(__file__).resolve().parent
REPO_ROOT = RUNNER_DIR.parents[2]
DEFAULT_TESTCASE_DIR = RUNNER_DIR / "test-cases"
DEFAULT_PACKAGE_DIR = REPO_ROOT / "qa" / "automation" / "testcases"
LOCAL_REPORT_DIR = REPO_ROOT / "qa" / "automation" / "reports" / "local"
ZEUZ_REPORT_DIR = REPO_ROOT / "qa" / "automation" / "reports" / "zeuz-compatible"
ADAPTER_CONFIG_PATH = REPO_ROOT / "qa" / "automation" / "config" / "zkme-adapters.json"
_ADAPTER_CONFIG_CACHE: dict[str, Any] | None = None


class StepFailure(Exception):
    pass


class PlaywrightSession:
    def __init__(self, testcase: dict[str, Any]) -> None:
        self.testcase = testcase
        self._playwright = None
        self._browser = None
        self._context = None
        self.page = None

    def start(self) -> Any:
        if self.page is not None:
            return self.page
        try:
            from playwright.sync_api import sync_playwright
        except Exception as exc:
            raise StepFailure("Playwright is not installed. Run: python -m pip install playwright && python -m playwright install") from exc
        config = self.testcase.get("playwright", {}) if isinstance(self.testcase.get("playwright"), dict) else {}
        browser_name = (config.get("browser") or "chromium").lower()
        headless = bool(config.get("headless", True))
        self._playwright = sync_playwright().start()
        browser_type = getattr(self._playwright, browser_name, self._playwright.chromium)
        self._browser = browser_type.launch(headless=headless)
        self._context = self._browser.new_context(base_url=config.get("baseURL") or None)
        self.page = self._context.new_page()
        return self.page

    def close(self) -> None:
        for obj in (self._context, self._browser):
            if obj is not None:
                try:
                    obj.close()
                except Exception:
                    pass
        if self._playwright is not None:
            try:
                self._playwright.stop()
            except Exception:
                pass


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _adapter_config() -> dict[str, Any]:
    global _ADAPTER_CONFIG_CACHE
    if _ADAPTER_CONFIG_CACHE is not None:
        return _ADAPTER_CONFIG_CACHE
    if ADAPTER_CONFIG_PATH.exists():
        try:
            _ADAPTER_CONFIG_CACHE = _load_json(ADAPTER_CONFIG_PATH)
        except Exception:
            _ADAPTER_CONFIG_CACHE = {}
    else:
        _ADAPTER_CONFIG_CACHE = {}
    return _ADAPTER_CONFIG_CACHE


def _get_adapter_config(adapter: str, testcase: dict[str, Any]) -> dict[str, Any]:
    config = ((_adapter_config().get("adapters") or {}).get(adapter) or {}).copy()
    testcase_config = testcase.get(adapter, {})
    if isinstance(testcase_config, dict):
        for key, value in testcase_config.items():
            if value not in (None, ""):
                config[key] = value
    return config


def _portable_entries_under(path: Path) -> list[Path]:
    entries = []
    entries.extend(sorted(candidate for candidate in path.glob("*.json") if candidate.name != "manifest.json"))
    entries.extend(sorted(path.glob("**/implementations/portable/testcase.json")))
    return entries


def _discover_testcases(paths: list[str]) -> list[Path]:
    if not paths:
        discovered = sorted(DEFAULT_TESTCASE_DIR.glob("*.json"))
        discovered.extend(sorted(DEFAULT_PACKAGE_DIR.glob("**/implementations/portable/testcase.json")))
        return discovered
    discovered: list[Path] = []
    for raw in paths:
        path = Path(raw)
        if path.is_dir():
            discovered.extend(_portable_entries_under(path))
        else:
            discovered.append(path)
    return discovered


def _load_portable_testcase(path: Path) -> tuple[dict[str, Any], Path]:
    payload = _load_json(path)
    schema = payload.get("schemaVersion")
    if schema == "zkme.portable-testcase.v1":
        return payload, path
    if schema == "zkme.test-package.v1":
        entry = ((payload.get("implementations") or {}).get("portable") or {}).get("entry")
        if not entry:
            raise StepFailure(f"Package manifest missing implementations.portable.entry: {path}")
        portable_path = path.parent / str(entry)
        return _load_portable_testcase(portable_path)
    if schema == "zkme.logical-testcase.v1":
        package_dir = path.parent
        manifest_path = package_dir / "manifest.json"
        if manifest_path.exists():
            return _load_portable_testcase(manifest_path)
        raise StepFailure(f"Logical testcase needs package manifest for execution: {path}")
    raise StepFailure(f"Unsupported testcase schema in {path}: {schema}")


def _join_url(base_url: str, url: str) -> str:
    if url.startswith(("http://", "https://")):
        return url
    return base_url.rstrip("/") + "/" + url.lstrip("/")


def _save_response_variables(step: dict[str, Any], response_data: Any, variables: Variables) -> None:
    save = step.get("save")
    if isinstance(save, dict):
        for name, value_path in save.items():
            value = response_data
            if isinstance(value_path, str) and value_path:
                for part in value_path.split("."):
                    if isinstance(value, dict):
                        value = value.get(part)
                    else:
                        value = None
                        break
            variables.set(str(name), value)


def _execute_api_step(step: dict[str, Any], testcase: dict[str, Any], variables: Variables) -> dict[str, Any]:
    step_input = variables.substitute(step.get("input", {}) if isinstance(step.get("input"), dict) else {})
    action = (step.get("action") or step_input.get("method") or "GET").upper()
    method = step_input.get("method", action).upper()
    base_url = testcase.get("baseURL") or testcase.get("api", {}).get("baseURL", "")
    url = _join_url(base_url, step_input.get("url") or step.get("url") or "")
    headers = dict(step_input.get("headers") or {})
    body = None
    if "json" in step_input:
        body = json.dumps(step_input["json"]).encode("utf-8")
        headers.setdefault("Content-Type", "application/json")
    elif "body" in step_input:
        raw_body = step_input["body"]
        body = raw_body.encode("utf-8") if isinstance(raw_body, str) else raw_body
    request = urllib.request.Request(url=url, method=method, data=body, headers=headers)
    expected_status = int(step_input.get("expectedStatus", step_input.get("status", 200)))
    try:
        with urllib.request.urlopen(request, timeout=int(step_input.get("timeoutSeconds", 30))) as response:
            status = int(response.status)
            raw = response.read().decode("utf-8", errors="replace")
            content_type = response.headers.get("content-type", "")
    except urllib.error.HTTPError as exc:
        status = int(exc.code)
        raw = exc.read().decode("utf-8", errors="replace")
        content_type = exc.headers.get("content-type", "")
    if status != expected_status:
        raise StepFailure(f"Expected HTTP {expected_status}, got {status}: {raw[:500]}")
    response_data: Any = raw
    if "json" in content_type:
        try:
            response_data = json.loads(raw)
        except json.JSONDecodeError:
            response_data = raw
    contains = step_input.get("expectedContains")
    if contains and str(contains) not in raw:
        raise StepFailure(f"Response did not contain expected text: {contains}")
    _save_response_variables(step, response_data, variables)
    return {"message": f"{method} {url} -> {status}"}


def _execute_db_step(step: dict[str, Any], testcase: dict[str, Any], variables: Variables) -> dict[str, Any]:
    step_input = variables.substitute(step.get("input", {}) if isinstance(step.get("input"), dict) else {})
    driver = (step_input.get("driver") or step_input.get("type") or "sqlite").lower()
    if driver != "sqlite":
        raise StepFailure(f"Only sqlite DB execution is supported by the default local runner. Requested: {driver}")
    db_path = Path(step_input.get("database") or step_input.get("dbPath") or testcase.get("database", {}).get("path", ""))
    if not db_path.is_absolute():
        db_path = REPO_ROOT / db_path
    sql = step_input.get("sql") or step_input.get("query") or step.get("action")
    if not sql:
        raise StepFailure("DB step missing sql/query")
    params = step_input.get("params") or []
    with sqlite3.connect(str(db_path)) as conn:
        cursor = conn.execute(sql, params)
        if sql.strip().lower().startswith("select"):
            rows = cursor.fetchall()
            expected_rows = step_input.get("expectedRows")
            if expected_rows is not None and len(rows) != int(expected_rows):
                raise StepFailure(f"Expected {expected_rows} row(s), got {len(rows)}")
            if step_input.get("saveFirstColumnAs") and rows:
                variables.set(step_input["saveFirstColumnAs"], rows[0][0])
            return {"message": f"SQLite query returned {len(rows)} row(s)"}
        conn.commit()
    return {"message": "SQLite statement executed"}


def _locator(page: Any, step: dict[str, Any]) -> Any:
    pw = step.get("playwright", {}) if isinstance(step.get("playwright"), dict) else {}
    locator = pw.get("locator") or step.get("selector")
    test_id = pw.get("testId")
    if test_id:
        return page.get_by_test_id(test_id)
    if not locator:
        raise StepFailure("Playwright step missing selector/playwright.locator")
    return page.locator(locator)


def _execute_playwright_step(step: dict[str, Any], testcase: dict[str, Any], variables: Variables, session: PlaywrightSession) -> dict[str, Any]:
    page = session.start()
    step_input = variables.substitute(step.get("input", {}) if isinstance(step.get("input"), dict) else {})
    pw = step.get("playwright", {}) if isinstance(step.get("playwright"), dict) else {}
    method = (pw.get("method") or step.get("action") or "").strip().lower()
    if method in {"go to link", "goto", "navigate", "open"}:
        url = step_input.get("url") or step.get("url") or step.get("selector") or "/"
        page.goto(url)
        return {"message": f"Navigated to {url}"}
    if method in {"click", "double click", "right click", "hover", "wait for element"}:
        target = _locator(page, step)
        if method == "double click":
            target.dblclick()
        elif method == "right click":
            target.click(button="right")
        elif method == "hover":
            target.hover()
        elif method == "wait for element":
            target.wait_for(timeout=int(pw.get("timeoutMs", 30000)))
        else:
            target.click()
        return {"message": method}
    if method in {"text", "fill", "clear and enter text"}:
        value = step_input.get("value", step_input.get("text", ""))
        _locator(page, step).fill(str(value))
        return {"message": "Filled text"}
    if method in {"validate full text", "validate partial text", "assert text", "expect text"}:
        expected = str(step_input.get("expectedText") or step.get("expected") or "")
        actual = _locator(page, step).inner_text(timeout=int(pw.get("timeoutMs", 30000)))
        if method == "validate full text" and actual.strip() != expected.strip():
            raise StepFailure(f"Expected exact text '{expected}', got '{actual}'")
        if expected not in actual:
            raise StepFailure(f"Expected text containing '{expected}', got '{actual}'")
        return {"message": "Text validated"}
    if method in {"take screenshot web", "screenshot"}:
        artifact_dir = ZEUZ_REPORT_DIR / "artifacts"
        artifact_dir.mkdir(parents=True, exist_ok=True)
        screenshot_path = artifact_dir / f"{step.get('id', 'step')}.png"
        page.screenshot(path=str(screenshot_path), full_page=True)
        return {"message": "Screenshot captured", "artifacts": [{"kind": "screenshot", "path": str(screenshot_path)}]}
    raise StepFailure(f"Unsupported Playwright action: {method}")


def _command_from_config(config: dict[str, Any]) -> list[str]:
    raw = config.get("command")
    if isinstance(raw, list):
        return [str(part) for part in raw if str(part).strip()]
    if isinstance(raw, str) and raw.strip():
        return shlex.split(raw)
    return []


def _execute_command_adapter(adapter: str, step: dict[str, Any], testcase: dict[str, Any], variables: Variables) -> dict[str, Any]:
    config = _get_adapter_config(adapter, testcase)
    if not config.get("enabled"):
        return {"status": "skipped", "message": f"{adapter} adapter is disabled in {ADAPTER_CONFIG_PATH}"}
    command = _command_from_config(config)
    if not command:
        return {"status": "skipped", "message": f"{adapter} adapter is enabled but no command is configured in {ADAPTER_CONFIG_PATH}"}
    payload = {
        "schemaVersion": "zkme.adapter-step-request.v1",
        "adapter": adapter,
        "testcase": {
            "id": testcase.get("id"),
            "title": testcase.get("title"),
            "targets": testcase.get("targets", []),
        },
        "step": variables.substitute(step),
        "config": {key: value for key, value in config.items() if key not in {"command", "env"}},
    }
    env = os.environ.copy()
    env.update({str(key): str(value) for key, value in (config.get("env") or {}).items()})
    env["ZKME_ADAPTER"] = adapter
    env["ZKME_TESTCASE_ID"] = str(testcase.get("id", ""))
    env["ZKME_STEP_ID"] = str(step.get("id", ""))
    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        timeout=int(config.get("timeoutSeconds", 120)),
        env=env,
        check=False,
    )
    stdout = completed.stdout.strip()
    stderr = completed.stderr.strip()
    parsed: dict[str, Any] = {}
    if stdout:
        try:
            loaded = json.loads(stdout)
            parsed = loaded if isinstance(loaded, dict) else {}
        except json.JSONDecodeError:
            parsed = {"message": stdout}
    message = str(parsed.get("message") or stdout or stderr or f"{adapter} command completed")
    status = str(parsed.get("status") or ("passed" if completed.returncode == 0 else "failed")).lower()
    if completed.returncode != 0 and status == "passed":
        status = "failed"
    if status == "failed":
        raise StepFailure(message)
    artifacts = parsed.get("artifacts", []) if isinstance(parsed.get("artifacts"), list) else []
    return {"status": status, "message": message, "artifacts": artifacts}


def _appium_by(strategy: str) -> str:
    strategy = strategy.strip().lower()
    mapping = {
        "accessibility id": "ACCESSIBILITY_ID",
        "accessibility_id": "ACCESSIBILITY_ID",
        "id": "ID",
        "xpath": "XPATH",
        "class name": "CLASS_NAME",
        "class_name": "CLASS_NAME",
        "android uiautomator": "ANDROID_UIAUTOMATOR",
        "ios predicate": "IOS_PREDICATE",
        "ios class chain": "IOS_CLASS_CHAIN",
    }
    return mapping.get(strategy, "ACCESSIBILITY_ID")


def _execute_appium_step(step: dict[str, Any], testcase: dict[str, Any], variables: Variables) -> dict[str, Any]:
    config = _get_adapter_config("mobile", testcase)
    if not config.get("enabled"):
        return {"status": "skipped", "message": f"mobile/Appium adapter is disabled in {ADAPTER_CONFIG_PATH}"}
    if _command_from_config(config):
        return _execute_command_adapter("mobile", step, testcase, variables)
    try:
        from appium import webdriver
        from appium.webdriver.common.appiumby import AppiumBy
    except Exception as exc:
        raise StepFailure("mobile adapter is enabled but the Appium Python client is not installed. Run: python -m pip install Appium-Python-Client") from exc
    remote_url = str(config.get("remoteUrl") or os.environ.get("APPIUM_SERVER_URL") or "http://127.0.0.1:4723")
    capabilities = config.get("capabilities") if isinstance(config.get("capabilities"), dict) else {}
    if not capabilities:
        raise StepFailure("mobile adapter is enabled but capabilities are empty in qa/automation/config/zkme-adapters.json")
    step_input = variables.substitute(step.get("input", {}) if isinstance(step.get("input"), dict) else {})
    selector = str(step_input.get("selector") or step.get("selector") or "")
    strategy = str(step_input.get("locatorStrategy") or config.get("locatorStrategy") or "accessibility id")
    action = str(step.get("action") or step_input.get("action") or "validate partial text").strip().lower()
    driver = webdriver.Remote(command_executor=remote_url, desired_capabilities=capabilities)
    try:
        if action in {"launch", "start app"}:
            return {"message": "Appium session launched"}
        if not selector:
            raise StepFailure("mobile/Appium step missing selector")
        by_name = _appium_by(strategy)
        by = getattr(AppiumBy, by_name)
        element = driver.find_element(by, selector)
        if action in {"click", "tap"}:
            element.click()
            return {"message": f"Tapped {selector}"}
        if action in {"text", "fill", "clear and enter text"}:
            value = str(step_input.get("value") or step_input.get("text") or "")
            element.clear()
            element.send_keys(value)
            return {"message": f"Entered text into {selector}"}
        if action in {"validate full text", "validate partial text", "assert text", "expect text"}:
            expected = str(step_input.get("expectedText") or step.get("expected") or "")
            actual = element.text or ""
            if action == "validate full text" and actual.strip() != expected.strip():
                raise StepFailure(f"Expected exact mobile text '{expected}', got '{actual}'")
            if expected not in actual:
                raise StepFailure(f"Expected mobile text containing '{expected}', got '{actual}'")
            return {"message": "Mobile text validated"}
        if action in {"screenshot", "take screenshot mobile"}:
            artifact_dir = ZEUZ_REPORT_DIR / "artifacts"
            artifact_dir.mkdir(parents=True, exist_ok=True)
            screenshot_path = artifact_dir / f"{step.get('id', 'mobile-step')}.png"
            driver.save_screenshot(str(screenshot_path))
            return {"message": "Mobile screenshot captured", "artifacts": [{"kind": "screenshot", "path": str(screenshot_path)}]}
        raise StepFailure(f"Unsupported Appium action: {action}")
    finally:
        if not config.get("keepSessionOpen"):
            try:
                driver.quit()
            except Exception:
                pass


def _execute_step(step: dict[str, Any], testcase: dict[str, Any], variables: Variables, session: PlaywrightSession) -> dict[str, Any]:
    adapter = (step.get("adapter") or "manual").strip().lower()
    if adapter == "api":
        return _execute_api_step(step, testcase, variables)
    if adapter == "db":
        return _execute_db_step(step, testcase, variables)
    if adapter == "playwright":
        return _execute_playwright_step(step, testcase, variables, session)
    if adapter in {"mobile", "appium"}:
        return _execute_appium_step(step, testcase, variables)
    if adapter in {"desktop", "performance", "security"}:
        return _execute_command_adapter(adapter, step, testcase, variables)
    if adapter == "manual":
        return {"status": "skipped", "message": "manual step recorded as candidate evidence"}
    raise StepFailure(f"Unsupported adapter: {adapter}")


def _run_testcase(path: Path) -> dict[str, Any]:
    testcase, executable_path = _load_portable_testcase(path)
    variables = Variables(testcase.get("variables") if isinstance(testcase.get("variables"), dict) else {})
    session = PlaywrightSession(testcase)
    started = utc_now()
    start_time = time.perf_counter()
    step_results: list[dict[str, Any]] = []
    try:
        for index, step in enumerate(testcase.get("steps", []), start=1):
            step_started = utc_now()
            step_start = time.perf_counter()
            status = "passed"
            message = ""
            artifacts = []
            try:
                details = _execute_step(step, testcase, variables, session)
                status = details.get("status", "passed")
                message = details.get("message", "")
                artifacts = details.get("artifacts", [])
            except Exception as exc:
                status = "failed"
                message = str(exc)
                if not step.get("continueOnFailure"):
                    step_results.append(_step_result(step, index, status, message, step_started, step_start, artifacts))
                    break
            step_results.append(_step_result(step, index, status, message, step_started, step_start, artifacts))
    finally:
        session.close()
    tc_status = aggregate_status([step["status"] for step in step_results])
    return {
        "id": testcase.get("id", executable_path.stem),
        "title": testcase.get("title", executable_path.stem),
        "status": tc_status,
        "portableTcPath": str(executable_path),
        "zeuzTcPath": testcase.get("zeuz", {}).get("testCaseId", ""),
        "evidence": testcase.get("evidence", []),
        "startedAt": started,
        "endedAt": utc_now(),
        "durationMs": int((time.perf_counter() - start_time) * 1000),
        "steps": step_results,
    }


def _step_result(step: dict[str, Any], index: int, status: str, message: str, started: str, start_time: float, artifacts: list[dict[str, Any]]) -> dict[str, Any]:
    mapping = step.get("zeuzMapping", {}) if isinstance(step.get("zeuzMapping"), dict) else {}
    step_key = step.get("stepKey") or step.get("id") or f"step-{index}"
    step_name = mapping.get("stepName") or step.get("stepName") or step.get("intent") or step.get("action") or f"Step {index}"
    return {
        "id": step_key,
        "stepKey": step_key,
        "name": step_name,
        "zeuzStepName": step_name,
        "status": status,
        "zeuzStepId": mapping.get("stepId") or index,
        "zeuzStepSequence": mapping.get("stepSequence") or index,
        "startedAt": started,
        "endedAt": utc_now(),
        "durationMs": int((time.perf_counter() - start_time) * 1000),
        "message": message,
        "artifacts": artifacts,
    }


def run(paths: list[str], environment: str = "local") -> Path:
    testcase_paths = _discover_testcases(paths)
    if not testcase_paths:
        raise SystemExit(f"No portable testcase JSON files found under {DEFAULT_TESTCASE_DIR}")
    run_id = "RUN-" + datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    started = utc_now()
    case_results = [_run_testcase(path) for path in testcase_paths]
    run_meta = {
        "id": run_id,
        "source": "local-zkme-runner",
        "startedAt": started,
        "endedAt": utc_now(),
        "environment": environment,
        "machine": platform.node(),
    }
    report = build_report(run_meta, case_results)
    LOCAL_REPORT_DIR.mkdir(parents=True, exist_ok=True)
    (LOCAL_REPORT_DIR / f"{run_id}.local-report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return write_report(report, ZEUZ_REPORT_DIR)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run ZKME portable testcases locally.")
    parser.add_argument("paths", nargs="*", help="Portable testcase JSON files or directories. Defaults to test-cases/*.json.")
    parser.add_argument("--environment", default="local", help="Environment label for the report.")
    args = parser.parse_args()
    report_path = run(args.paths, environment=args.environment)
    print(f"Wrote ZeuZ-compatible report: {report_path}")


if __name__ == "__main__":
    main()
