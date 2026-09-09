from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from spirt.evidence import Evidence


@dataclass(slots=True)
class SocialProfile:
    """Normalized representation of publicly available profile information."""

    platform: str
    profile_url: str
    username: str | None = None
    display_name: str | None = None
    profile_id: str | None = None
    bio: str | None = None
    location: str | None = None
    website: str | None = None
    links: list[str] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        return {
            "platform": self.platform,
            "profile_url": self.profile_url,
            "username": self.username,
            "display_name": self.display_name,
            "profile_id": self.profile_id,
            "bio": self.bio,
            "location": self.location,
            "website": self.website,
            "links": list(self.links),
            "evidence": [item.to_dict() for item in self.evidence],
            "metadata": dict(self.metadata),
        }
