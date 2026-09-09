from unittest.mock import patch

from spirt.collection import CollectionStatus
from spirt.http import FetchError
from spirt.models import SocialProfile
from spirt.providers.facebook import FacebookProvider
from spirt.providers.registry import get_provider, list_providers

FIXTURE_HTML = """<!doctype html><html><head>
<meta property="og:title" content="Example User">
<meta property="og:url" content="https://www.facebook.com/example">
<meta property="og:description" content="A public profile example">
<meta property="og:image" content="https://example.com/profile.jpg">
<script type="application/ld+json">{"@type":"Person","name":"Example User"}</script>
</head></html>"""


def test_facebook_provider_supports_profile_url() -> None:
    assert FacebookProvider().supports("https://www.facebook.com/example")


def test_facebook_provider_rejects_non_facebook_url() -> None:
    assert not FacebookProvider().supports("https://example.com/profile")


def test_provider_registry_returns_facebook() -> None:
    assert get_provider("https://facebook.com/example").name == "facebook"


def test_registry_contains_v04_platforms() -> None:
    assert {p.name for p in list_providers()} == {"facebook", "instagram", "linkedin", "x", "tiktok", "github"}


def test_facebook_collect_returns_success_result() -> None:
    with patch("spirt.providers.facebook.fetch_text", return_value=FIXTURE_HTML):
        result = FacebookProvider().collect("https://www.facebook.com/example")
    assert result.status is CollectionStatus.SUCCESS
    assert isinstance(result.data, SocialProfile)
    assert result.data.username == "example"
    assert result.data.display_name == "Example User"
    assert result.data.bio == "A public profile example"
    assert result.data.metadata["collection_status"] == "success"
    assert result.data.metadata["public_image"] == "https://example.com/profile.jpg"


def test_facebook_collect_reports_fetch_failure() -> None:
    with patch("spirt.providers.facebook.fetch_text", side_effect=FetchError("network failure")):
        result = FacebookProvider().collect("https://www.facebook.com/example")
    assert result.status is CollectionStatus.UNAVAILABLE
    assert result.error == "network failure"
    assert result.data.metadata["collection_status"] == "unavailable"


def test_facebook_collect_reports_parse_failure() -> None:
    with patch("spirt.providers.facebook.fetch_text", return_value=object()):
        result = FacebookProvider().collect("https://www.facebook.com/example")
    assert result.status is CollectionStatus.FAILED
    assert result.data is None
    assert result.error
