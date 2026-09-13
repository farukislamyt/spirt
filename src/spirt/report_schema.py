from __future__ import annotations

from typing import Any

REPORT_SCHEMA_VERSION = "1.0"
REPORT_TOOL = "SPIRT"


def validate_report(report: dict[str, Any]) -> None:
    """Validate the stable top-level report contract."""
    if not isinstance(report, dict):
        raise TypeError("report must be a dictionary")
    if report.get("tool") != REPORT_TOOL:
        raise ValueError("report.tool must be SPIRT")
    if report.get("schema_version") != REPORT_SCHEMA_VERSION:
        raise ValueError(f"unsupported report schema version: {report.get('schema_version')!r}")
    if not isinstance(report.get("generated_at"), str) or not report["generated_at"].strip():
        raise ValueError("report.generated_at must be a non-empty string")
    for key in ("results", "correlations", "evidence_graph", "timeline"):
        if not isinstance(report.get(key), list):
            raise ValueError(f"report.{key} must be a list")


def report_json_schema() -> dict[str, Any]:
    """Return a JSON-Schema-compatible description of the report envelope."""
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://github.com/farukislamyt/spirt/schema/report-1.0.json",
        "title": "SPIRT Research Report",
        "type": "object",
        "required": ["tool", "schema_version", "generated_at", "results", "correlations", "evidence_graph", "timeline"],
        "properties": {
            "tool": {"const": REPORT_TOOL},
            "schema_version": {"const": REPORT_SCHEMA_VERSION},
            "generated_at": {"type": "string"},
            "results": {"type": "array"},
            "correlations": {"type": "array"},
            "evidence_graph": {"type": "array"},
            "timeline": {"type": "array"},
        },
        "additionalProperties": True,
    }
