import pytest

from spirt.collection import CollectionErrorCode, CollectionResult, CollectionStatus
from spirt.models import SocialProfile
from spirt.providers import Provider, host_matches, parse_provider_url
from spirt.providers.metadata import MetadataProvider, ProviderCapabilities


class FakeProvider(Provider):
    name = "fake"

    def supports(self, url: str) -> bool:
        parsed = parse_provider_url(url)
        return parsed is not None and host_matches(parsed, frozenset({"fake.example"}))

    def collect(self, url: str) -> CollectionResult:
        if not self.supports(url):
            return CollectionResult(
                CollectionStatus.FAILED,
                error="Unsupported fake URL",
                error_code=CollectionErrorCode.UNSUPPORTED_URL,
            )
        return CollectionResult(CollectionStatus.SUCCESS, SocialProfile(platform=self.name, profile_url=url))


def test_provider_contract_is_platform_agnostic() -> None:
    provider = FakeProvider()
    assert provider.supports("https://fake.example/alice")
    result = provider.collect("https://fake.example/alice")
    assert result.status is CollectionStatus.SUCCESS
    assert result.data.platform == "fake"


def test_provider_url_parser_rejects_credentials_and_non_https() -> None:
    assert parse_provider_url("https://user:pass@fake.example/alice") is None
    assert parse_provider_url("http://fake.example/alice") is None
    assert parse_provider_url("https://fake.example:bad/alice") is None


def test_host_matching_uses_exact_domain_boundaries() -> None:
    parsed = parse_provider_url("https://fake.example/alice")
    assert parsed is not None
    assert host_matches(parsed, frozenset({"fake.example"}))
    evil = parse_provider_url("https://notfake.example/alice")
    assert evil is not None
    assert not host_matches(evil, frozenset({"fake.example"}))


def test_capabilities_validate_declarations() -> None:
    with pytest.raises(ValueError, match="platform"):
        ProviderCapabilities(platform=" ", hosts=frozenset({"fake.example"}))
    with pytest.raises(ValueError, match="hosts"):
        ProviderCapabilities(platform="fake", hosts=frozenset())
    with pytest.raises(ValueError, match="valid domain"):
        ProviderCapabilities(platform="fake", hosts=frozenset({"localhost"}))
    with pytest.raises(ValueError, match="capability"):
        ProviderCapabilities(platform="fake", hosts=frozenset({"fake.example"}), public_web_metadata=False)


def test_metadata_provider_requires_matching_platform_name() -> None:
    with pytest.raises(ValueError, match="match"):
        MetadataProvider(
            name="fake",
            capabilities=ProviderCapabilities(platform="other", hosts=frozenset({"fake.example"})),
        )


def test_unsupported_collection_returns_structured_failure() -> None:
    result = FakeProvider().collect("https://other.example/alice")
    assert result.status is CollectionStatus.FAILED
    assert result.error_code is CollectionErrorCode.UNSUPPORTED_URL


def test_collection_result_success_rejects_error() -> None:
    profile = SocialProfile(platform="fake", profile_url="https://fake.example/alice")
    with pytest.raises(ValueError, match="cannot contain an error"):
        CollectionResult(CollectionStatus.SUCCESS, data=profile, error="unexpected")
