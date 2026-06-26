"""Build and write ZKME ZeuZ-compatible local reports."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .status import aggregate_status, normalize_status, zeuz_status


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def duration_text(duration_ms: int | float | None) -> str:
    total = int((duration_ms or 0) / 1000)
    hours = total // 3600
    minutes = (total % 3600) // 60
    seconds = total % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def _summary(test_cases: list[dict[str, Any]]) -> dict[str, Any]:
    statuses = [normalize_status(tc.get("status")) for tc in test_cases]
    return {
        "status": aggregate_status(statuses),
        "passed": sum(1 for status in statuses if status == "passed"),
        "failed": sum(1 for status in statuses if status == "failed"),
        "skipped": sum(1 for status in statuses if status == "skipped"),
        "durationMs": int(sum(tc.get("durationMs", 0) or 0 for tc in test_cases)),
    }


def _zeuz_step(step: dict[str, Any], index: int) -> dict[str, Any]:
    duration_ms = int(step.get("durationMs", 0) or 0)
    return {
        "step_id": int(step.get("zeuzStepId") or index),
        "step_sequence": int(step.get("zeuzStepSequence") or index),
        "step_key": step.get("stepKey") or step.get("id") or f"step-{index}",
        "name": step.get("zeuzStepName") or step.get("name") or step.get("id") or f"Step {index}",
        "execution_detail": {
            "stepstarttime": step.get("startedAt") or "",
            "stependtime": step.get("endedAt") or "",
            "duration": duration_text(duration_ms),
            "status": zeuz_status(step.get("status")),
            "logid": step.get("logid") or "",
        },
    }


def _zeuz_test_case(test_case: dict[str, Any]) -> dict[str, Any]:
    duration_ms = int(test_case.get("durationMs", 0) or 0)
    steps = test_case.get("steps", [])
    return {
        "testcase_no": test_case.get("id", ""),
        "title": test_case.get("title", test_case.get("id", "")),
        "execution_detail": {
            "teststarttime": test_case.get("startedAt") or "",
            "testendtime": test_case.get("endedAt") or "",
            "duration": duration_text(duration_ms),
            "status": zeuz_status(test_case.get("status")),
            "failreason": test_case.get("message") or "",
            "logid": test_case.get("logid") or "",
        },
        "steps": [_zeuz_step(step, index) for index, step in enumerate(steps, start=1)],
    }


def build_report(run: dict[str, Any], test_cases: list[dict[str, Any]]) -> dict[str, Any]:
    summary = _summary(test_cases)
    run_id = run.get("id", "")
    return {
        "schemaVersion": "zkme.zeuz-compatible-report.v1",
        "run": {
            "id": run_id,
            "source": run.get("source", "local-zkme-runner"),
            "startedAt": run.get("startedAt") or utc_now(),
            "endedAt": run.get("endedAt") or utc_now(),
            "environment": run.get("environment", "local"),
            "machine": run.get("machine", ""),
            "browser": run.get("browser", ""),
            "device": run.get("device", ""),
            "zeuzRunId": run.get("zeuzRunId", run_id),
        },
        "zeuzImport": {
            "serverRequired": False,
            "status": "ready-for-import",
            "testCaseImportTarget": "/gql/graphql testing.testCase.*",
            "resultImportTarget": "/api/v1/tasks/update-test-results",
            "artifactImportTarget": "/api/v1/tasks/process-report-files",
            "nativeResultPath": "zeuzExecutionLog[].test_cases[].execution_detail",
            "nativeStepResultPath": "zeuzExecutionLog[].test_cases[].steps[].execution_detail",
        },
        "summary": summary,
        "testCases": test_cases,
        "zeuzExecutionLog": [
            {
                "run_id": run_id,
                "machine_name": run.get("machine", ""),
                "execution_detail": {
                    "status": zeuz_status(summary["status"]),
                    "teststarttime": run.get("startedAt") or "",
                    "testendtime": run.get("endedAt") or "",
                    "duration": duration_text(summary["durationMs"]),
                },
                "test_cases": [_zeuz_test_case(test_case) for test_case in test_cases],
            }
        ],
    }


def write_report(report: dict[str, Any], output_dir: Path, name: str | None = None) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    run_id = report.get("run", {}).get("id", "RUN-local")
    filename = name or f"{run_id}.zeuz-report.json"
    path = output_dir / filename
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path
