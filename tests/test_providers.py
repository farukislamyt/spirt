from spirt.models import SocialProfile
from spirt.providers.facebook import FacebookProvider
from spirt.providers.registry import get_provider


def test_facebook_provider_supports_profile_url() -> None:
    provider = FacebookProvider()
    assert provider.supports("https://www.facebook.com/example")


def test_facebook_provider_rejects_non_facebook_url() -> None:
    provider = FacebookProvider()
    assert not provider.supports("https://example.com/profile")


def test_provider_registry_returns_facebook() -> None:
    assert get_provider("https://facebook.com/example").name == "facebook"


def test_facebook_target_extracts_username() -> None:
    profile = FacebookProvider().collect("https://www.facebook.com/example")
    assert isinstance(profile, SocialProfile)
    assert profile.username == "example"
    assert profile.metadata["collection_status"] == "target_only"
