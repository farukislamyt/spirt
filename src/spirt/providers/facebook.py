from __future__ import annotations

from urllib.parse import urlparse

from spirt.evidence import Evidence
from spirt.http import FetchError, fetch_text
from spirt.models import SocialProfile
from spirt.parsers import first_json_ld_value, parse_json_ld, parse_public_metadata
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
        display_name = (
            metadata.get("og:title")
            or metadata.get("twitter:title")
            or first_json_ld_value(json_ld, "name")
            or metadata.get("title")
        )
        bio = metadata.get("og:description") or metadata.get("description")
        canonical = metadata.get("og:url") or url
        image = metadata.get("og:image") or metadata.get("twitter:image")
        website = metadata.get("og:see_also") or metadata.get("profile:website")

        evidence: list[Evidence] = []
        if display_name:
            evidence.append(Evidence("display_name", display_name, canonical, method="open_graph"))
        if bio:
            evidence.append(Evidence("bio", bio, canonical, method="open_graph"))
        if image:
            evidence.append(Evidence("public_image", image, canonical, method="open_graph"))
        if website:
            evidence.append(Evidence("website", website, canonical, method="open_graph"))

        return SocialProfile(
            platform=self.name,
            profile_url=canonical,
            username=username,
            display_name=display_name,
            bio=bio,
            website=website,
            links=[canonical],
            evidence=evidence,
            metadata={
                "collection_status": "success",
                "source": {"type": "public_webpage", "url": url},
                "open_graph": metadata,
                "json_ld": json_ld,
            },
        )
