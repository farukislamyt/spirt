from pathlib import Path

from spirt.parsers import first_json_ld_value, parse_json_ld, parse_public_metadata

FIXTURE = Path(__file__).parent / "fixtures" / "facebook_public_profile.html"


def test_parse_public_metadata() -> None:
    html = FIXTURE.read_text(encoding="utf-8")
    metadata = parse_public_metadata(html)
    assert metadata["og:title"] == "Example User"
    assert metadata["og:url"] == "https://www.facebook.com/example"
    assert metadata["og:description"] == "A public profile example"
    assert metadata["title"] == "Example User | Facebook"


def test_parse_metadata_when_content_precedes_property() -> None:
    html = '<meta content="Example" property="og:title">'
    assert parse_public_metadata(html)["og:title"] == "Example"


def test_parse_json_ld() -> None:
    html = FIXTURE.read_text(encoding="utf-8")
    data = parse_json_ld(html)
    assert data[0]["@type"] == "Person"
    assert data[0]["name"] == "Example User"
    assert first_json_ld_value(data, "name") == "Example User"


def test_parse_json_ld_ignores_invalid_json() -> None:
    html = '<script type="application/ld+json">not-json</script>'
    assert parse_json_ld(html) == []
