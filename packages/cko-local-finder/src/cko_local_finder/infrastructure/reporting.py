"""Deterministic UTF-8 JSON serialization for internal report values."""

from dataclasses import asdict, is_dataclass
import json
from typing import Any


def report_dict(report: Any) -> dict[str, Any]:
    if not is_dataclass(report):
        raise TypeError("report must be a dataclass value")
    return asdict(report)


def report_json(report: Any) -> str:
    return json.dumps(report_dict(report), ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")) + "\n"
