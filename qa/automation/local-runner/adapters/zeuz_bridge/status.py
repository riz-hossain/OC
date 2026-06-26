"""Status mapping between ZKME local runner and ZeuZ reports."""

from __future__ import annotations


ZKME_TO_ZEUZ = {
    "passed": "Passed",
    "failed": "Failed",
    "skipped": "Skipped",
    "blocked": "Blocked",
}


def normalize_status(status: str | None) -> str:
    value = (status or "").strip().lower()
    if value in {"pass", "passed", "ok", "success"}:
        return "passed"
    if value in {"fail", "failed", "error", "zeuz_failed"}:
        return "failed"
    if value in {"skip", "skipped"}:
        return "skipped"
    if value in {"block", "blocked"}:
        return "blocked"
    return "failed"


def zeuz_status(status: str | None) -> str:
    return ZKME_TO_ZEUZ.get(normalize_status(status), "Failed")


def aggregate_status(statuses: list[str]) -> str:
    normalized = [normalize_status(status) for status in statuses]
    if any(status == "failed" for status in normalized):
        return "failed"
    if any(status == "blocked" for status in normalized):
        return "blocked"
    if normalized and all(status == "skipped" for status in normalized):
        return "skipped"
    return "passed"
