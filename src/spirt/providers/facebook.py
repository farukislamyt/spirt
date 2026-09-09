from __future__ import annotations

from urllib.parse import urlparse

from spirt.models import SocialProfile
from spirt.providers import Provider


class FacebookProvider(Provider):
    """Handle Facebook profile URLs without bypassing access controls."""

    name = "facebook"
    _hosts = {"facebook.com", "www.facebook.com", "m.facebook.com", "mbasic.facebook.com"}

    def supports(self, url: str) -> bool:
        """Return True for Facebook HTTPS profile URLs."""
        parsed = urlparse(url)
        return parsed.scheme == "https" and parsed.hostname in self._hosts

    def collect(self, url: str) -> SocialProfile:
        """Create a normalized profile target from a Facebook URL.

        Network collection is intentionally not performed yet. Future collection
        must use legitimately public data or an authorized official API.
        """
        if not self.supports(url):
            raise ValueError("Unsupported Facebook URL")

        path_parts = [part for part in urlparse(url).path.split("/") if part]
        username = path_parts[0] if path_parts and path_parts[0] not in {"profile.php"} else None

        return SocialProfile(
            platform=self.name,
            profile_url=url,
            username=username,
            metadata={"collection_status": "target_only"},
        )
