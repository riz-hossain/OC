"""Variable substitution helpers for portable ZKME testcases."""

from __future__ import annotations

import re
from typing import Any


VAR_PATTERN = re.compile(r"%\|([^|]+)\|%")


class Variables:
    def __init__(self, initial: dict[str, Any] | None = None) -> None:
        self.values: dict[str, Any] = dict(initial or {})

    def set(self, name: str, value: Any) -> None:
        self.values[name] = value

    def get(self, name: str, default: Any = "") -> Any:
        return self.values.get(name, default)

    def substitute(self, value: Any) -> Any:
        if isinstance(value, str):
            return VAR_PATTERN.sub(lambda match: str(self.get(match.group(1), "")), value)
        if isinstance(value, list):
            return [self.substitute(item) for item in value]
        if isinstance(value, dict):
            return {key: self.substitute(item) for key, item in value.items()}
        return value
