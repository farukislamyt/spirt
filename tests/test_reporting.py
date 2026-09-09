from spirt.collection import CollectionResult, CollectionStatus
from spirt.models import SocialProfile
from spirt.reporting import render_report_json, render_report_markdown


def test_report_renderers_include_profiles_and_status() -> None:
    result = CollectionResult(CollectionStatus.SUCCESS, SocialProfile(platform="github", profile_url="https://github.com/alice", username="alice"))
    assert "github" in render_report_json([result])
    assert "SPIRT Research Report" in render_report_markdown([result])
