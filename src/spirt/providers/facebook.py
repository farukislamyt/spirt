from __future__ import annotations

from typing import ClassVar
from urllib.parse import urlparse

from spirt.collection import CollectionResult, CollectionStatus
from spirt.http import FetchError, fetch_text
from spirt.models import SocialProfile
from spirt.normalizers import normalize_profile
from spirt.parsers import parse_json_ld, parse_public_metadata
from spirt.providers import Provider, host_matches, parse_provider_url


class FacebookProvider(Provider):
    """Research metadata that is publicly exposed by a Facebook profile page."""

    name = "facebook"
    _hosts: ClassVar[frozenset[str]] = frozenset(
        {"facebook.com", "www.facebook.com", "m.facebook.com", "mbasic.facebook.com"}
    )

    def supports(self, url: str) -> bool:
        """Return True only for valid HTTPS Facebook profile URLs."""
        parsed = parse_provider_url(url)
        return parsed is not None and host_matches(parsed, self._hosts)

    def collect(self, url: str) -> CollectionResult:
        """Fetch and normalize publicly exposed page metadata."""
        if not self.supports(url):
            raise ValueError("Unsupported Facebook URL")

        parts = [part for part in urlparse(url).path.split("/") if part]
        username = parts[0] if parts and parts[0] != "profile.php" else None

        try:
            html = fetch_text(url)
        except FetchError as exc:
            profile = SocialProfile(
                platform=self.name,
                profile_url=url,
                username=username,
                metadata={"collection_status": CollectionStatus.UNAVAILABLE.value, "error": str(exc)},
            )
            return CollectionResult(CollectionStatus.UNAVAILABLE, data=profile, error=str(exc))

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
        except (KeyError, TypeError, ValueError) as exc:
            return CollectionResult(CollectionStatus.FAILED, error=str(exc))

        return CollectionResult(CollectionStatus.SUCCESS, data=profile)
