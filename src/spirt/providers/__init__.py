from __future__ import annotations

from abc import ABC, abstractmethod
from urllib.parse import SplitResult, urlsplit

from spirt.collection import CollectionResult


class Provider(ABC):
    """Interface implemented by social-profile providers."""

    name: str

    @abstractmethod
    def supports(self, url: str) -> bool:
        """Return whether this provider can handle the supplied URL."""

    @abstractmethod
    def collect(self, url: str) -> CollectionResult:
        """Collect publicly available information from a supported profile."""


def parse_provider_url(url: str) -> SplitResult | None:
    """Parse a provider URL without performing network access.

    Provider routing is intentionally syntax-only; DNS/IP safety is enforced by
    the HTTP fetch layer immediately before a public document is requested.
    """
    if not isinstance(url, str) or not url.strip():
        return None
    try:
        parsed = urlsplit(url)
        if parsed.scheme.lower() != "https" or not parsed.hostname:
            return None
        if parsed.username is not None or parsed.password is not None:
            return None
        try:
            parsed.port
        except ValueError:
            return None
    except ValueError:
        return None
    return parsed


def host_matches(parsed: SplitResult, hosts: frozenset[str]) -> bool:
    """Return True only when the parsed hostname exactly matches a capability."""
    hostname = parsed.hostname
    if not hostname:
        return False
    return hostname.rstrip(".").lower() in hosts


__all__ = ["Provider", "host_matches", "parse_provider_url"]
