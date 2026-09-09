from unittest.mock import patch

from typer.testing import CliRunner

from spirt.cli import app
from spirt.evidence import Evidence
from spirt.models import SocialProfile

runner = CliRunner()


def test_profile_json_includes_evidence() -> None:
    profile = SocialProfile(
        platform="facebook",
        profile_url="https://www.facebook.com/example",
        username="example",
        display_name="Example User",
        evidence=[Evidence("display_name", "Example User", "https://www.facebook.com/example", method="open_graph")],
    )
    with patch("spirt.cli.get_provider") as get_provider:
        get_provider.return_value.collect.return_value = profile
        result = runner.invoke(app, ["profile", "https://www.facebook.com/example", "--json"])

    assert result.exit_code == 0
    assert '"evidence"' in result.stdout
    assert '"method": "open_graph"' in result.stdout


def test_profile_evidence_flag_renders_provenance() -> None:
    profile = SocialProfile(
        platform="facebook",
        profile_url="https://www.facebook.com/example",
        display_name="Example User",
        evidence=[Evidence("display_name", "Example User", "https://www.facebook.com/example", method="open_graph")],
    )
    with patch("spirt.cli.get_provider") as get_provider:
        get_provider.return_value.collect.return_value = profile
        result = runner.invoke(app, ["profile", "https://www.facebook.com/example", "--evidence"])

    assert result.exit_code == 0
    assert "Evidence" in result.stdout
    assert "open_graph" in result.stdout


def test_profile_collection_error_returns_nonzero() -> None:
    with patch("spirt.cli.get_provider") as get_provider:
        get_provider.return_value.collect.side_effect = RuntimeError("temporary failure")
        result = runner.invoke(app, ["profile", "https://www.facebook.com/example"])

    assert result.exit_code == 1
    assert "Collection failed" in result.stdout
