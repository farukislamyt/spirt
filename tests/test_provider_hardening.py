import pytest

from spirt.collection import CollectionErrorCode, CollectionStatus
from spirt.providers import host_matches, parse_provider_url
from spirt.providers.metadata import MetadataProvider, ProviderCapabilities


def test_parse_provider_url_is_network_free_and_strict() -> None:
    assert parse_provider_url("https://example.com/profile") is not None
    assert parse_provider_url("http://example.com/profile") is None
    assert parse_provider_url("https://user:pass@example.com/profile") is None
    assert parse_provider_url("https://example.com:bad/profile") is None
    assert parse_provider_url("") is None


def test_host_matching_requires_exact_domain_boundary() -> None:
    parsed = parse_provider_url("https://facebook.com/profile")
    assert parsed is not None
    assert host_matches(parsed, frozenset({"facebook.com"}))

    attacker = parse_provider_url("https://evilfacebook.com/profile")
    assert attacker is not None
    assert not host_matches(attacker, frozenset({"facebook.com"}))


def test_provider_capabilities_normalize_hosts() -> None:
    capabilities = ProviderCapabilities(
        platform="example",
        hosts=frozenset({" Example.COM. "}),
    )
    assert capabilities.hosts == frozenset({"example.com"})


@pytest.mark.parametrize(
    "kwargs",
    [
        {"platform": "", "hosts": frozenset({"example.com"})},
        {"platform": "example", "hosts": frozenset()},
        {"platform": "example", "hosts": frozenset({"localhost"})},
        {
            "platform": "example",
            "hosts": frozenset(),
            "public_web_metadata": False,
            "official_api": False,
        },
    ],
)
def test_provider_capabilities_reject_invalid_declarations(kwargs: dict) -> None:
    with pytest.raises(ValueError):
        ProviderCapabilities(**kwargs)


def test_metadata_provider_requires_matching_name() -> None:
    capabilities = ProviderCapabilities(platform="example", hosts=frozenset({"example.com"}))
    with pytest.raises(ValueError, match="match"):
        MetadataProvider(name="other", capabilities=capabilities)


def test_metadata_provider_rejects_unsafe_hosts_without_network_access() -> None:
    provider = MetadataProvider(
        name="example",
        capabilities=ProviderCapabilities(platform="example", hosts=frozenset({"example.com"})),
    )
    assert not provider.supports("https://evil.example.com/profile")
    assert not provider.supports("https://user:pass@example.com/profile")


def test_metadata_provider_unsupported_url_returns_structured_error() -> None:
    provider = MetadataProvider(
        name="example",
        capabilities=ProviderCapabilities(platform="example", hosts=frozenset({"example.com"})),
    )
    result = provider.collect("https://other.example/profile")
    assert result.status is CollectionStatus.FAILED
    assert result.error_code is CollectionErrorCode.UNSUPPORTED_URL
