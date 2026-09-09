from __future__ import annotations

from urllib.parse import urlparse

from spirt.http import FetchError, fetch_text
from spirt.models import SocialProfile
from spirt.parsers import parse_json_ld, parse_public_metadata
from spirt.providers import Provider


class FacebookProvider(Provider):
    """Research metadata that is publicly exposed by a Facebook profile page."""

    name = "facebook"
    _hosts = {"facebook.com", "www.facebook.com", "m.facebook.com", "mbasic.facebook.com"}

    def supports(self, url: str) -> bool:
        """Return True for Facebook HTTPS profile URLs."""
        parsed = urlparse(url)
        return parsed.scheme == "https" and parsed.hostname in self._hosts

    def collect(self, url: str) -> SocialProfile:
        """Fetch and parse publicly exposed page metadata."""
        if not self.supports(url):
            raise ValueError("Unsupported Facebook URL")

        parts = [part for part in urlparse(url).path.split("/") if part]
        username = parts[0] if parts and parts[0] != "profile.php" else None

        try:
            html = fetch_text(url)
        except FetchError as exc:
            return SocialProfile(
                platform=self.name,
                profile_url=url,
                username=username,
                metadata={"collection_status": "unavailable", "error": str(exc)},
            )

        metadata = parse_public_metadata(html)
        json_ld = parse_json_ld(html)
        display_name = metadata.get("og:title") or metadata.get("twitter:title") or metadata.get("title")
        canonical = metadata.get("og:url") or url
        image = metadata.get("og:image")

        return SocialProfile(
            platform=self.name,
            profile_url=canonical,
            username=username,
            display_name=display_name,
            links=[canonical],
            metadata={
                "collection_status": "success",
                "open_graph": metadata,
                "json_ld": json_ld,
                **({"public_image": image} if image else {}),
            },
        )
