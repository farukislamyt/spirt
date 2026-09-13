import pytest

from spirt.providers import host_matches, parse_provider_url
from spirt.providers.metadata import MetadataProvider, ProviderCapabilities


def test_parse_provider_url_rejects_unsafe_provider_inputs() -> None:
    assert parse_provider_url("http://example.com/profile") is None
    assert parse_provider_url("https://user:pass@example.com/profile") is None
    assert parse_provider_url("https://example.com:bad/profile") is None
    assert parse_provider_url("") is None


def test_parse_provider_url_is_case_insensitive() -> None:
    parsed = parse_provider_url("HTTPS://Example.COM/Alice")
    assert parsed is not None
    assert parsed.hostname == "example.com"


def test_host_matches_requires_exact_domain_boundary() -> None:
    parsed = parse_provider_url("https://facebook.com/alice")
    assert parsed is not None
    hosts = frozenset({"facebook.com"})
    assert host_matches(parsed, hosts)

    evil = parse_provider_url("https://notfacebook.com/alice")
    assert evil is not None
    assert not host_matches(evil, hosts)


def test_capabilities_normalize_hosts() -> None:
    capabilities = ProviderCapabilities(
        platform="example",
        hosts=frozenset({"Example.COM.", "www.Example.COM"}),
    )
    assert capabilities.hosts == frozenset({"example.com", "www.example.com"})


@pytest.mark.parametrize(
    "kwargs",
    [
        {"platform": "", "hosts": frozenset({"example.com"})},
        {"platform": "example", "hosts": frozenset()},
        {"platform": "example", "hosts": frozenset({"localhost"})},
        {"platform": "example", "hosts": frozenset({"example.com"}), "public_web_metadata": False},
    ],
)
def test_capabilities_reject_invalid_declarations(kwargs: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        ProviderCapabilities(**kwargs)


def test_metadata_provider_requires_matching_capability_platform() -> None:
    capabilities = ProviderCapabilities(platform="instagram", hosts=frozenset({"instagram.com"}))
    with pytest.raises(ValueError, match="match"):
        MetadataProvider(name="facebook", capabilities=capabilities)


def test_metadata_provider_rejects_credentials_and_host_suffix_tricks() -> None:
    provider = MetadataProvider(
        name="example",
        capabilities=ProviderCapabilities(platform="example", hosts=frozenset({"example.com"})),
    )
    assert provider.supports("https://example.com/alice")
    assert not provider.supports("https://user:pass@example.com/alice")
    assert not provider.supports("https://example.com.evil.test/alice")
