from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from urllib.parse import urlparse

from spirt.collection import CollectionResult, CollectionStatus
from spirt.http import FetchError, fetch_text
from spirt.models import SocialProfile
from spirt.normalizers import normalize_profile
from spirt.parsers import parse_json_ld, parse_public_metadata
from spirt.providers import Provider, host_matches, parse_provider_url


@dataclass(frozen=True, slots=True)
class ProviderCapabilities:
    """Describes what a provider can safely collect."""

    platform: str
    hosts: frozenset[str]
    public_web_metadata: bool = True
    official_api: bool = False
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.platform.strip():
            raise ValueError("provider platform must not be empty")
        if not self.hosts:
            raise ValueError("provider hosts must not be empty")
        normalized = frozenset(host.strip().lower().rstrip(".") for host in self.hosts)
        if any(not host or "." not in host for host in normalized):
            raise ValueError("provider hosts must be valid domain names")
        object.__setattr__(self, "hosts", normalized)
        if not self.public_web_metadata and not self.official_api:
            raise ValueError("provider must declare at least one collection capability")


@dataclass(slots=True)
class MetadataProvider(Provider):
    """Generic public-web metadata provider used by platform adapters."""

    name: str
    capabilities: ProviderCapabilities
    _hosts: frozenset[str] = field(init=False)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("provider name must not be empty")
        if self.name != self.capabilities.platform:
            raise ValueError("provider name must match capability platform")
        object.__setattr__(self, "_hosts", self.capabilities.hosts)

    def supports(self, url: str) -> bool:
        """Return True only for valid HTTPS URLs on declared provider hosts."""
        parsed = parse_provider_url(url)
        return parsed is not None and host_matches(parsed, self._hosts)

    def collect(self, url: str) -> CollectionResult:
        if not self.supports(url):
            raise ValueError(f"Unsupported {self.name} URL")
        parts = [part for part in urlparse(url).path.split("/") if part]
        username = parts[0] if parts else None
        try:
            html = fetch_text(url)
        except FetchError as exc:
            return CollectionResult(
                CollectionStatus.UNAVAILABLE,
                data=SocialProfile(
                    platform=self.name,
                    profile_url=url,
                    username=username,
                    metadata={"collection_status": CollectionStatus.UNAVAILABLE.value, "error": str(exc)},
                ),
                error=str(exc),
            )
        try:
            metadata = parse_public_metadata(html)
            json_ld = parse_json_ld(html)
            profile = normalize_profile(
                platform=self.name,
                profile_url=url,
                username=username,
                metadata={
                    "collection_status": CollectionStatus.SUCCESS.value,
                    "source": {"type": "public_webpage", "url": url},
                    "open_graph": metadata,
                    "json_ld": json_ld,
                },
                json_ld=json_ld,
            )
            return CollectionResult(CollectionStatus.SUCCESS, data=profile)
        except (KeyError, TypeError, ValueError) as exc:
            return CollectionResult(CollectionStatus.FAILED, error=str(exc))


def platform_provider(name: str, hosts: Iterable[str], notes: str) -> MetadataProvider:
    return MetadataProvider(
        name=name,
        capabilities=ProviderCapabilities(
            platform=name,
            hosts=frozenset(hosts),
            notes=notes,
        ),
    )
