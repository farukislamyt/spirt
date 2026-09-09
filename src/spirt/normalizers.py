from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from urllib.parse import urlparse

from spirt.evidence import Evidence
from spirt.models import SocialProfile


def _first_text(*values: Any) -> str | None:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def normalize_profile(
    *,
    platform: str,
    profile_url: str,
    username: str | None = None,
    metadata: Mapping[str, Any] | None = None,
    json_ld: list[dict[str, Any]] | None = None,
) -> SocialProfile:
    """Normalize provider metadata into the canonical SPIRT profile model."""
    metadata = dict(metadata or {})
    json_ld = list(json_ld or [])
    open_graph = metadata.get("open_graph", {})
    if not isinstance(open_graph, Mapping):
        open_graph = {}

    display_name = _first_text(
        open_graph.get("og:title"),
        open_graph.get("twitter:title"),
        next((obj.get("name") for obj in json_ld if isinstance(obj.get("name"), str)), None),
        open_graph.get("title"),
    )
    bio = _first_text(open_graph.get("og:description"), open_graph.get("description"))
    canonical = _first_text(open_graph.get("og:url"), profile_url) or profile_url
    website = _first_text(open_graph.get("og:see_also"), open_graph.get("profile:website"))
    image = _first_text(open_graph.get("og:image"), open_graph.get("twitter:image"))

    if username is None:
        path_parts = [part for part in urlparse(canonical).path.split("/") if part]
        username = path_parts[0] if path_parts and path_parts[0] != "profile.php" else None

    evidence = [
        Evidence("display_name", display_name, canonical, method="normalized_metadata")
        for _ in [0]
        if display_name
    ]
    if bio:
        evidence.append(Evidence("bio", bio, canonical, method="normalized_metadata"))
    if website:
        evidence.append(Evidence("website", website, canonical, method="normalized_metadata"))
    if image:
        evidence.append(Evidence("public_image", image, canonical, method="normalized_metadata"))

    normalized_metadata = dict(metadata)
    normalized_metadata["normalization"] = {
        "version": 1,
        "fields": {
            "display_name": "og:title|twitter:title|json_ld.name|title",
            "bio": "og:description|description",
            "website": "og:see_also|profile:website",
            "public_image": "og:image|twitter:image",
        },
    }

    return SocialProfile(
        platform=platform,
        profile_url=canonical,
        username=username,
        display_name=display_name,
        bio=bio,
        website=website,
        links=[canonical],
        evidence=evidence,
        metadata=normalized_metadata,
    )
