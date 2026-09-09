from unittest.mock import patch

from spirt.models import SocialProfile
from spirt.providers.facebook import FacebookProvider
from spirt.providers.registry import get_provider


FIXTURE_HTML = """<!doctype html><html><head>
<meta property="og:title" content="Example User">
<meta property="og:url" content="https://www.facebook.com/example">
<meta property="og:description" content="A public profile example">
<meta property="og:image" content="https://example.com/profile.jpg">
<script type="application/ld+json">{"@type":"Person","name":"Example User"}</script>
</head></html>"""


def test_facebook_provider_supports_profile_url() -> None:
    provider = FacebookProvider()
    assert provider.supports("https://www.facebook.com/example")


def test_facebook_provider_rejects_non_facebook_url() -> None:
    provider = FacebookProvider()
    assert not provider.supports("https://example.com/profile")


def test_provider_registry_returns_facebook() -> None:
    assert get_provider("https://facebook.com/example").name == "facebook"


def test_facebook_collect_normalizes_public_fields() -> None:
    with patch("spirt.providers.facebook.fetch_text", return_value=FIXTURE_HTML):
        profile = FacebookProvider().collect("https://www.facebook.com/example")

    assert isinstance(profile, SocialProfile)
    assert profile.username == "example"
    assert profile.display_name == "Example User"
    assert profile.bio == "A public profile example"
    assert profile.profile_url == "https://www.facebook.com/example"
    assert profile.metadata["collection_status"] == "success"
    assert profile.metadata["source"]["type"] == "public_webpage"
    assert profile.metadata["public_image"] == "https://example.com/profile.jpg"


def test_facebook_collect_reports_fetch_failure() -> None:
    with patch("spirt.providers.facebook.fetch_text", side_effect=Exception("network failure")):
        try:
            FacebookProvider().collect("https://www.facebook.com/example")
        except Exception as exc:
            assert str(exc) == "network failure"
