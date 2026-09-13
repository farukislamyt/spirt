import json

import pytest

from spirt.collection import CollectionResult, CollectionStatus
from spirt.models import SocialProfile
from spirt.report_schema import REPORT_SCHEMA_VERSION, validate_report
from spirt.reporting import render_report_html, render_report_json, render_report_markdown


def _result() -> CollectionResult:
    return CollectionResult(
        CollectionStatus.SUCCESS,
        SocialProfile(platform="github", profile_url="https://github.com/alice", username="alice"),
    )


def test_report_renderers_include_profiles_and_status() -> None:
    result = _result()
    assert "github" in render_report_json([result])
    assert "SPIRT Research Report" in render_report_markdown([result])
    assert "<html" in render_report_html([result])


def test_json_report_has_stable_schema_and_sorted_keys() -> None:
    rendered = render_report_json([_result()], generated_at="2026-01-01T00:00:00+00:00")
    report = json.loads(rendered)
    validate_report(report)
    assert report["schema_version"] == REPORT_SCHEMA_VERSION
    assert list(report) == sorted(report)
    assert report["timeline"][0]["platform"] == "github"


def test_report_validation_rejects_wrong_version() -> None:
    report = {
        "tool": "SPIRT",
        "schema_version": "0.1",
        "generated_at": "now",
        "results": [],
        "correlations": [],
        "evidence_graph": [],
        "timeline": [],
    }
    with pytest.raises(ValueError, match="unsupported report schema version"):
        validate_report(report)
