#!/usr/bin/env python
"""Validate and sync ZKME-generated ZeuZ drafts and local reports.

The script is generated into every ZKME-enabled repository. It is intentionally
stdlib-only so local execution, dry-run export, and CI validation work before a
project has ZeuZ Server credentials.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ZEUZ_DIR = Path(__file__).resolve().parent
REPO_ROOT = ZEUZ_DIR.parents[2]
DRAFT_DIR = ZEUZ_DIR / "test-cases"
PACKAGE_DIR = REPO_ROOT / "qa" / "automation" / "testcases"
LOCAL_RUN_DIR = ZEUZ_DIR / "local-run"
REPORT_DIR = REPO_ROOT / "qa" / "automation" / "reports" / "zeuz-compatible"

IMPORT_TESTCASES_ENDPOINT = "/api/v1/tasks/import-testcases"
UPDATE_RESULTS_ENDPOINT = "/api/v1/tasks/update-test-results"
PROCESS_REPORT_FILES_ENDPOINT = "/api/v1/tasks/process-report-files"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def print_payload(payload: Any, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    if isinstance(payload, dict):
        status = payload.get("status", "ok")
        counts = payload.get("counts") or {}
        print(f"status={status} counts={counts}")
        if payload.get("outputPath"):
            print(f"output={payload['outputPath']}")
        if payload.get("errors"):
            for error in payload["errors"]:
                print(f"ERROR: {error}", file=sys.stderr)


def _path_from_user(raw: str) -> Path:
    path = Path(raw)
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path


def _draft_candidates_under(path: Path) -> list[Path]:
    candidates = []
    candidates.extend(sorted(path.glob("**/*.zeuz-draft.json")))
    candidates.extend(sorted(path.glob("**/implementations/zeuz-actions/actions.json")))
    return candidates


def discover_draft_paths(raw_paths: list[str]) -> list[Path]:
    if not raw_paths:
        paths = sorted(DRAFT_DIR.glob("**/*.zeuz-draft.json"))
        paths.extend(sorted(PACKAGE_DIR.glob("**/implementations/zeuz-actions/actions.json")))
        return paths
    paths: list[Path] = []
    for raw in raw_paths:
        path = _path_from_user(raw)
        if path.is_dir():
            paths.extend(_draft_candidates_under(path))
        else:
            paths.append(path)
    return paths


def _draft_from_zeuz_actions(payload: dict[str, Any], source_path: Path) -> dict[str, Any]:
    draft = payload.get("draftTestcase") if isinstance(payload.get("draftTestcase"), dict) else {}
    if draft:
        draft = dict(draft)
        draft.setdefault("_sourcePath", str(source_path))
        return draft
    return {
        "schemaVersion": "zkme.zeuz-draft-testcase.v1",
        "id": payload.get("testcaseId") or payload.get("id"),
        "title": payload.get("title") or payload.get("testcaseId") or source_path.parent.parent.parent.name,
        "risk": payload.get("risk", "medium"),
        "confidence": payload.get("confidence", "medium"),
        "targets": payload.get("targets", ["zeuz"]),
        "evidence": payload.get("evidence", []),
        "zeuz": payload.get("zeuz", {}),
        "steps": payload.get("steps", []),
        "generatedBy": payload.get("generatedBy", "ZKME"),
        "_sourcePath": str(source_path),
    }


def load_drafts(paths: list[Path]) -> tuple[list[dict[str, Any]], list[str]]:
    drafts: list[dict[str, Any]] = []
    errors: list[str] = []
    for path in paths:
        try:
            payload = load_json(path)
        except Exception as exc:
            errors.append(f"{path}: invalid JSON: {exc}")
            continue
        if isinstance(payload, dict) and payload.get("schemaVersion") == "zkme.zeuz-draft-suite.v1":
            for item in payload.get("testCases", []):
                if isinstance(item, dict):
                    item.setdefault("_sourcePath", str(path))
                    drafts.append(item)
            continue
        if isinstance(payload, dict) and payload.get("schemaVersion") == "zkme.zeuz-actions-implementation.v1":
            drafts.append(_draft_from_zeuz_actions(payload, path))
            continue
        if isinstance(payload, dict):
            payload.setdefault("_sourcePath", str(path))
            drafts.append(payload)
        else:
            errors.append(f"{path}: expected object or zkme.zeuz-draft-suite.v1")
    return drafts, errors


def validate_draft(draft: dict[str, Any]) -> tuple[list[str], list[str]]:
    source = draft.get("_sourcePath", "<memory>")
    errors: list[str] = []
    warnings: list[str] = []
    if draft.get("schemaVersion") != "zkme.zeuz-draft-testcase.v1":
        errors.append(f"{source}: schemaVersion must be zkme.zeuz-draft-testcase.v1")
    if not draft.get("id"):
        errors.append(f"{source}: missing id")
    if not draft.get("title"):
        errors.append(f"{source}: missing title")
    steps = draft.get("steps")
    if not isinstance(steps, list) or not steps:
        errors.append(f"{source}: missing steps")
        return errors, warnings
    seen_step_names: set[str] = set()
    for index, step in enumerate(steps, start=1):
        if not isinstance(step, dict):
            errors.append(f"{source}: step {index} is not an object")
            continue
        step_name = str(step.get("stepName") or step.get("name") or "").strip()
        if not step_name:
            warnings.append(f"{source}: step {index} missing name")
        elif step_name in seen_step_names:
            errors.append(f"{source}: duplicate ZeuZ step name {step_name!r}; ZeuZ requires unique step names inside a testcase")
        seen_step_names.add(step_name)
        if not step.get("stepKey") and not step.get("id"):
            errors.append(f"{source}: step {index} missing stepKey/id")
        if not step.get("actionName") and not step.get("actionLabel"):
            warnings.append(f"{source}: step {index} has no ZeuZ actionName/actionLabel")
        rows = step.get("rows")
        if rows is not None and not isinstance(rows, list):
            errors.append(f"{source}: step {index} rows must be a list")
    return errors, warnings


def validate_drafts(raw_paths: list[str]) -> dict[str, Any]:
    paths = discover_draft_paths(raw_paths)
    drafts, load_errors = load_drafts(paths)
    errors = list(load_errors)
    warnings: list[str] = []
    for draft in drafts:
        draft_errors, draft_warnings = validate_draft(draft)
        errors.extend(draft_errors)
        warnings.extend(draft_warnings)
    return {
        "schemaVersion": "zkme.zeuz-sync-validation.v1",
        "status": "failed" if errors else "passed",
        "generatedAt": utc_now(),
        "draftPaths": [str(path) for path in paths],
        "counts": {
            "drafts": len(drafts),
            "errors": len(errors),
            "warnings": len(warnings),
        },
        "errors": errors,
        "warnings": warnings,
    }


def _priority_from_risk(risk: str) -> str:
    return {"critical": "P1", "high": "P1", "medium": "P2", "low": "P3"}.get(str(risk).lower(), "P2")


def _automatable_from_targets(targets: list[Any]) -> str:
    lowered = {str(target).lower() for target in targets}
    if lowered & {"playwright", "api", "db", "mobile", "desktop", "performance", "security"}:
        return "automated"
    return "easily automatable"


def _step_automatable(source_adapter: str) -> str:
    adapter = source_adapter.lower()
    if adapter == "playwright":
        return "Web"
    if adapter == "mobile":
        return "Mobile"
    if adapter == "desktop":
        return "Desktop"
    if adapter in {"api", "db", "database"}:
        return "API"
    return "Desktop"


def _row_objects(rows: Any) -> list[dict[str, Any]]:
    row_objects: list[dict[str, Any]] = []
    if not isinstance(rows, list):
        return row_objects
    for index, row in enumerate(rows, start=1):
        if isinstance(row, list):
            data = [str(value) for value in row[:3]]
        elif isinstance(row, dict):
            raw = row.get("data", [])
            data = [str(value) for value in raw[:3]] if isinstance(raw, list) else [str(raw), "", ""]
        else:
            data = [str(row), "", ""]
        while len(data) < 3:
            data.append("")
        row_objects.append({"sequence": index, "data": data})
    return row_objects


def _import_step(step: dict[str, Any], sequence: int, total_steps: int) -> dict[str, Any]:
    source_adapter = str(step.get("sourceAdapter") or "manual")
    action_name = str(step.get("actionName") or step.get("actionLabel") or "manual candidate")
    step_key = str(step.get("stepKey") or step.get("id") or f"step-{sequence}")
    step_name = str(step.get("stepName") or step.get("name") or step_key or f"Step {sequence}")
    rows = _row_objects(step.get("rows"))
    return {
        "sequence": int(step.get("sequence") or sequence),
        "name": step_name,
        "description": "\n".join(
            [
                f"Source adapter: {source_adapter}",
                f"ZKME action: {action_name}",
                f"ZKME stepKey: {step_key}",
                f"ZeuZ stepName: {step_name}",
            ]
        ).strip(),
        "expected": str(step.get("expected") or "Expected result is defined by the generated ZKME testcase."),
        "type": "normal",
        "verifyPoint": bool(sequence == total_steps),
        "continuePoint": False,
        "stepInfo": {
            "driver": "Built_In_Driver",
            "stepType": "automated",
            "dataRequired": bool(rows),
            "stepEnable": True,
            "stepEditable": True,
            "automatable": _step_automatable(source_adapter),
            "estdTime": "59",
        },
        "actions": [
            {
                "sequence": 1,
                "name": action_name,
                "enabled": True,
                "rows": rows,
            }
        ],
    }


def draft_to_import_case(draft: dict[str, Any]) -> dict[str, Any]:
    zeuz = draft.get("zeuz") if isinstance(draft.get("zeuz"), dict) else {}
    raw_steps = [step for step in draft.get("steps", []) if isinstance(step, dict)]
    steps = [_import_step(step, index, len(raw_steps)) for index, step in enumerate(raw_steps, start=1)]
    return {
        "testCaseDetail": {
            "id": str(draft.get("id")),
            "name": str(draft.get("title") or draft.get("id")),
            "priority": _priority_from_risk(str(draft.get("risk") or "medium")),
            "status": "Dev",
            "testCaseType": "Automated" if "manual" not in draft.get("targets", []) else "Manual",
            "automatability": _automatable_from_targets(draft.get("targets", [])),
            "time": "00:00:59",
        },
        "folder_name": str(zeuz.get("folder") or "ZKME Generated"),
        "feature_name": str(zeuz.get("feature") or draft.get("title") or "ZKME Generated"),
        "steps": steps,
        "zkme": {
            "schemaVersion": draft.get("schemaVersion"),
            "sourcePath": draft.get("_sourcePath"),
            "targets": draft.get("targets", []),
            "evidence": draft.get("evidence", []),
            "confidence": draft.get("confidence", ""),
            "stepIdentity": "stepKey",
            "stepBindings": {
                str(step.get("stepKey") or step.get("id") or f"step-{index}"): {
                    "stepName": str(step.get("stepName") or step.get("name") or f"Step {index}"),
                    "sequence": int(step.get("sequence") or index),
                    "zeuzStepId": None,
                }
                for index, step in enumerate(raw_steps, start=1)
            },
        },
    }


def build_draft_import_bundle(args: argparse.Namespace) -> dict[str, Any]:
    paths = discover_draft_paths(args.draft)
    drafts, load_errors = load_drafts(paths)
    validation_errors: list[str] = list(load_errors)
    validation_warnings: list[str] = []
    for draft in drafts:
        draft_errors, draft_warnings = validate_draft(draft)
        validation_errors.extend(draft_errors)
        validation_warnings.extend(draft_warnings)
    import_cases = [draft_to_import_case(draft) for draft in drafts if not validate_draft(draft)[0]]
    payload = {
        "test_cases": import_cases,
        "test_case_ids": [case["testCaseDetail"]["id"] for case in import_cases],
        "attachment_data": {},
        "step_attachment_data": {},
        "step_rename_dict": {},
        "project_id": args.project_id,
        "team_id": int(args.team_id) if str(args.team_id).isdigit() else args.team_id,
        "user_id": int(args.user_id) if str(args.user_id).isdigit() else args.user_id,
        "user_name": args.user_name,
        "set_name": args.set_name,
        "extraction_path": "",
    }
    return {
        "schemaVersion": "zkme.zeuz-import-bundle.v1",
        "generatedAt": utc_now(),
        "mode": "draft-testcase-import",
        "dryRun": not args.execute,
        "serverUrl": args.server_url or "",
        "endpoint": {"method": "POST", "path": IMPORT_TESTCASES_ENDPOINT},
        "payload": payload,
        "sourceDraftPaths": [str(path) for path in paths],
        "validation": {
            "errors": validation_errors,
            "warnings": validation_warnings,
        },
        "counts": {
            "drafts": len(drafts),
            "importCases": len(import_cases),
            "steps": sum(len(case.get("steps", [])) for case in import_cases),
        },
    }


def _report_paths(raw_paths: list[str]) -> list[Path]:
    if raw_paths:
        return [_path_from_user(raw) for raw in raw_paths]
    return sorted(REPORT_DIR.glob("RUN-*.zeuz-report.json"))


def _resolve_artifact_path(raw_path: str, report_path: Path) -> Path | None:
    if not raw_path:
        return None
    candidates = []
    path = Path(raw_path)
    if path.is_absolute():
        candidates.append(path)
    else:
        candidates.append(report_path.parent / path)
        candidates.append(REPO_ROOT / path)
    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate
    return candidates[0] if candidates else None


def collect_report_artifacts(report: dict[str, Any], report_path: Path) -> tuple[dict[str, Any], list[dict[str, Any]], int]:
    file_data: dict[str, Any] = {}
    artifacts: list[dict[str, Any]] = []
    total_size = 0
    for test_case in report.get("testCases", []):
        if not isinstance(test_case, dict):
            continue
        tc_id = str(test_case.get("id") or "unknown")
        for step_index, step in enumerate(test_case.get("steps", []) or [], start=1):
            if not isinstance(step, dict):
                continue
            for artifact_index, artifact in enumerate(step.get("artifacts", []) or [], start=1):
                if not isinstance(artifact, dict):
                    continue
                artifact_path = _resolve_artifact_path(str(artifact.get("path") or ""), report_path)
                exists = bool(artifact_path and artifact_path.exists())
                size = artifact_path.stat().st_size if exists and artifact_path else 0
                total_size += size
                key = f"{tc_id}__step{step_index}__artifact{artifact_index}"
                item = {
                    "testCaseId": tc_id,
                    "stepId": step.get("id", ""),
                    "stepKey": step.get("stepKey") or step.get("id", ""),
                    "zeuzStepName": step.get("zeuzStepName") or step.get("name", ""),
                    "kind": artifact.get("kind", "log"),
                    "path": str(artifact_path) if artifact_path else str(artifact.get("path") or ""),
                    "exists": exists,
                    "size": size,
                }
                artifacts.append(item)
                if exists and artifact_path:
                    file_data[key] = {
                        "content": base64.b64encode(artifact_path.read_bytes()).decode("ascii"),
                        "filename": artifact_path.name,
                        "kind": item["kind"],
                        "path": item["path"],
                    }
    return file_data, artifacts, total_size


def build_result_import_bundle(args: argparse.Namespace) -> dict[str, Any]:
    reports = []
    result_payloads = []
    artifact_payloads = []
    errors: list[str] = []
    for report_path in _report_paths(args.report):
        try:
            report = load_json(report_path)
        except Exception as exc:
            errors.append(f"{report_path}: invalid JSON: {exc}")
            continue
        if report.get("schemaVersion") != "zkme.zeuz-compatible-report.v1":
            errors.append(f"{report_path}: schemaVersion must be zkme.zeuz-compatible-report.v1")
            continue
        run_id = str(report.get("run", {}).get("id") or report.get("zeuzExecutionLog", [{}])[0].get("run_id") or report_path.stem)
        zeuz_execution_log = report.get("zeuzExecutionLog") or []
        result_payloads.append(
            {
                "run_id": run_id,
                "json_data": zeuz_execution_log,
                "milestone": args.milestone,
                "version": args.version,
                "project_id": args.project_id,
                "team_id": int(args.team_id) if str(args.team_id).isdigit() else args.team_id,
                "user_id": int(args.user_id) if str(args.user_id).isdigit() else args.user_id,
            }
        )
        file_data, artifacts, total_size = collect_report_artifacts(report, report_path)
        artifact_payloads.append(
            {
                "run_id": run_id,
                "file_data": file_data,
                "base_dirs": {
                    "repo_root": str(REPO_ROOT),
                    "report_dir": str(report_path.parent),
                },
                "team_id": int(args.team_id) if str(args.team_id).isdigit() else args.team_id,
                "project_id": args.project_id,
                "user_id": int(args.user_id) if str(args.user_id).isdigit() else args.user_id,
                "file_size": total_size,
                "zkme_artifacts": artifacts,
            }
        )
        reports.append({"path": str(report_path), "runId": run_id, "artifacts": len(artifacts)})
    return {
        "schemaVersion": "zkme.zeuz-result-import-bundle.v1",
        "generatedAt": utc_now(),
        "mode": "local-report-import",
        "dryRun": not args.execute,
        "serverUrl": args.server_url or "",
        "endpoints": [
            {"method": "POST", "path": UPDATE_RESULTS_ENDPOINT},
            {"method": "POST", "path": PROCESS_REPORT_FILES_ENDPOINT},
        ],
        "reports": reports,
        "resultPayloads": result_payloads,
        "artifactPayloads": artifact_payloads,
        "validation": {"errors": errors, "warnings": []},
        "counts": {
            "reports": len(reports),
            "resultPayloads": len(result_payloads),
            "artifactPayloads": len(artifact_payloads),
            "artifacts": sum(len(payload.get("zkme_artifacts", [])) for payload in artifact_payloads),
            "encodedArtifacts": sum(len(payload.get("file_data", {})) for payload in artifact_payloads),
        },
    }


def auth_headers(api_token: str | None) -> dict[str, str]:
    headers = {"Content-Type": "application/json"}
    if api_token:
        token = api_token.strip()
        headers["X-API-KEY"] = token
        headers["Authorization"] = token if token.lower().startswith(("bearer ", "token ")) else f"Bearer {token}"
    return headers


def post_json(server_url: str, endpoint: str, payload: dict[str, Any], api_token: str | None) -> dict[str, Any]:
    url = server_url.rstrip("/") + endpoint
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=data, headers=auth_headers(api_token), method="POST")
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            raw = response.read().decode("utf-8", errors="replace")
            try:
                body = json.loads(raw)
            except json.JSONDecodeError:
                body = {"raw": raw}
            return {"ok": 200 <= int(response.status) < 300, "status": int(response.status), "body": body, "url": url}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            body = json.loads(raw)
        except json.JSONDecodeError:
            body = {"raw": raw}
        return {"ok": False, "status": int(exc.code), "body": body, "url": url}


def execute_draft_import(bundle: dict[str, Any], args: argparse.Namespace) -> list[dict[str, Any]]:
    return [post_json(args.server_url, IMPORT_TESTCASES_ENDPOINT, bundle["payload"], args.api_token)]


def execute_result_import(bundle: dict[str, Any], args: argparse.Namespace) -> list[dict[str, Any]]:
    responses: list[dict[str, Any]] = []
    for payload in bundle.get("resultPayloads", []):
        responses.append(post_json(args.server_url, UPDATE_RESULTS_ENDPOINT, payload, args.api_token))
    for payload in bundle.get("artifactPayloads", []):
        if payload.get("file_data"):
            responses.append(post_json(args.server_url, PROCESS_REPORT_FILES_ENDPOINT, payload, args.api_token))
    return responses


def add_common_sync_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--server-url", default=os.environ.get("ZEUZ_SERVER_URL", ""), help="ZeuZ Server base URL.")
    parser.add_argument("--api-token", default=os.environ.get("ZEUZ_API_TOKEN") or os.environ.get("ZEUZ_API_KEY") or "", help="ZeuZ API token/key.")
    parser.add_argument("--project-id", default=os.environ.get("ZEUZ_PROJECT_ID", ""), help="ZeuZ project id.")
    parser.add_argument("--team-id", default=os.environ.get("ZEUZ_TEAM_ID", ""), help="ZeuZ team id.")
    parser.add_argument("--user-id", default=os.environ.get("ZEUZ_USER_ID", ""), help="ZeuZ user id.")
    parser.add_argument("--execute", action="store_true", help="POST payloads to ZeuZ Server. Default is dry-run only.")
    parser.add_argument("--out", default="", help="Write generated bundle to this path.")
    parser.add_argument("--json", action="store_true", help="Print full JSON output.")


def require_execute_args(parser: argparse.ArgumentParser, args: argparse.Namespace, require_user_name: bool = False) -> None:
    if not args.execute:
        return
    missing = []
    for name in ("server_url", "project_id", "team_id", "user_id"):
        if not getattr(args, name):
            missing.append("--" + name.replace("_", "-"))
    if require_user_name and not args.user_name:
        missing.append("--user-name")
    if missing:
        parser.error("--execute requires " + ", ".join(missing))


def command_validate_drafts(args: argparse.Namespace) -> int:
    result = validate_drafts(args.draft)
    print_payload(result, args.json)
    return 0 if result["status"] == "passed" else 1


def command_push_drafts(args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
    require_execute_args(parser, args, require_user_name=True)
    bundle = build_draft_import_bundle(args)
    if args.out:
        path = write_json(_path_from_user(args.out), bundle)
    else:
        path = write_json(LOCAL_RUN_DIR / "zkme-zeuz-draft-import-bundle.json", bundle)
    bundle["outputPath"] = str(path)
    if bundle["validation"]["errors"]:
        print_payload({**bundle, "status": "failed"}, args.json)
        return 1
    if args.execute:
        bundle["responses"] = execute_draft_import(bundle, args)
    print_payload({**bundle, "status": "ready" if not args.execute else "submitted"}, args.json)
    return 0


def command_push_results(args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
    require_execute_args(parser, args)
    bundle = build_result_import_bundle(args)
    if args.out:
        path = write_json(_path_from_user(args.out), bundle)
    else:
        path = write_json(LOCAL_RUN_DIR / "zkme-zeuz-result-import-bundle.json", bundle)
    bundle["outputPath"] = str(path)
    if bundle["validation"]["errors"]:
        print_payload({**bundle, "status": "failed"}, args.json)
        return 1
    if args.execute:
        bundle["responses"] = execute_result_import(bundle, args)
    print_payload({**bundle, "status": "ready" if not args.execute else "submitted"}, args.json)
    return 0


def command_export_bundle(args: argparse.Namespace) -> int:
    draft_args = argparse.Namespace(**vars(args))
    draft_args.execute = False
    result_args = argparse.Namespace(**vars(args))
    result_args.execute = False
    bundle = {
        "schemaVersion": "zkme.zeuz-offline-sync-bundle.v1",
        "generatedAt": utc_now(),
        "project": "OC",
        "draftImport": build_draft_import_bundle(draft_args),
        "resultImport": build_result_import_bundle(result_args),
    }
    out = _path_from_user(args.out or "qa/automation/zeuz/local-run/zkme-zeuz-offline-sync-bundle.json")
    write_json(out, bundle)
    print_payload({"status": "ready", "outputPath": str(out), "counts": {"drafts": bundle["draftImport"]["counts"]["drafts"], "reports": bundle["resultImport"]["counts"]["reports"]}}, args.json)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate and sync ZKME ZeuZ-compatible drafts/reports.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate-drafts", help="Validate generated .zeuz-draft.json files.")
    validate.add_argument("draft", nargs="*", help="Draft file or directory. Defaults to qa/automation/zeuz/test-cases/**/*.zeuz-draft.json.")
    validate.add_argument("--json", action="store_true")

    push_drafts = subparsers.add_parser("push-drafts", help="Build or submit /api/v1/tasks/import-testcases payloads.")
    push_drafts.add_argument("draft", nargs="*", help="Draft file or directory.")
    add_common_sync_args(push_drafts)
    push_drafts.add_argument("--user-name", default=os.environ.get("ZEUZ_USER_NAME", ""), help="ZeuZ username for import audit.")
    push_drafts.add_argument("--set-name", default=os.environ.get("ZEUZ_SET_NAME", ""), help="Optional ZeuZ test set name.")

    push_results = subparsers.add_parser("push-results", help="Build or submit local report result/artifact payloads.")
    push_results.add_argument("report", nargs="*", help="Report file. Defaults to qa/automation/reports/zeuz-compatible/RUN-*.zeuz-report.json.")
    add_common_sync_args(push_results)
    push_results.add_argument("--milestone", default=os.environ.get("ZEUZ_MILESTONE", ""))
    push_results.add_argument("--version", default=os.environ.get("ZEUZ_VERSION", ""))

    export_bundle = subparsers.add_parser("export-bundle", help="Build one offline bundle with drafts, reports, and artifacts.")
    export_bundle.add_argument("--draft", action="append", default=[], help="Draft path. Can be repeated.")
    export_bundle.add_argument("--report", action="append", default=[], help="Report path. Can be repeated.")
    export_bundle.add_argument("--out", default="", help="Output path.")
    export_bundle.add_argument("--json", action="store_true")
    export_bundle.set_defaults(
        server_url="",
        api_token="",
        project_id="",
        team_id="",
        user_id="",
        user_name="",
        set_name="",
        milestone="",
        version="",
        execute=False,
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "validate-drafts":
        return command_validate_drafts(args)
    if args.command == "push-drafts":
        return command_push_drafts(args, parser)
    if args.command == "push-results":
        return command_push_results(args, parser)
    if args.command == "export-bundle":
        return command_export_bundle(args)
    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
