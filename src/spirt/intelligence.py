from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from urllib.parse import urlsplit

from spirt.models import SocialProfile


@dataclass(frozen=True, slots=True)
class ResolvedTarget:
    """A deterministic set of candidate profile URLs for one research target."""

    query: str
    candidates: tuple[str, ...]
    normalized: str

    def to_dict(self) -> dict[str, object]:
        return {"query": self.query, "normalized": self.normalized, "candidates": list(self.candidates)}


@dataclass(frozen=True, slots=True)
class EntityMatch:
    """Explainable similarity between two normalized profiles."""

    left_platform: str
    right_platform: str
    score: float
    reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "left_platform": self.left_platform,
            "right_platform": self.right_platform,
            "score": self.score,
            "reasons": list(self.reasons),
        }


@dataclass(frozen=True, slots=True)
class EvidenceEdge:
    """A typed, explainable relationship between two profile observations."""

    left_platform: str
    left_url: str
    right_platform: str
    right_url: str
    signal: str
    weight: float

    def to_dict(self) -> dict[str, object]:
        return {
            "left_platform": self.left_platform,
            "left_url": self.left_url,
            "right_platform": self.right_platform,
            "right_url": self.right_url,
            "signal": self.signal,
            "weight": self.weight,
        }


def resolve_target(query: str, *, templates: tuple[str, ...] = ()) -> ResolvedTarget:
    """Normalize a username/profile URL and build deterministic URL candidates.

    This resolver never performs network access. Templates must contain one
    ``{username}`` placeholder and should point only at known public hosts.
    """
    if not isinstance(query, str) or not query.strip():
        raise ValueError("target query must not be empty")
    value = query.strip()
    parsed = urlsplit(value)
    normalized = value.casefold()
    if parsed.scheme:
        if parsed.scheme.lower() != "https" or not parsed.hostname:
            raise ValueError("target URL must be an absolute HTTPS URL")
        if parsed.username is not None or parsed.password is not None:
            raise ValueError("target URL must not contain credentials")
        normalized = value.rstrip("/")
        candidates = (normalized,)
    else:
        username = value.lstrip("@").strip()
        if not username:
            raise ValueError("target username must not be empty")
        if any(char.isspace() for char in username):
            raise ValueError("target username must not contain whitespace")
        candidates = tuple(template.format(username=username) for template in templates)
        normalized = username.casefold()
    return ResolvedTarget(query=value, candidates=candidates, normalized=normalized)


def _shared_links(left: SocialProfile, right: SocialProfile) -> bool:
    left_links = {link.casefold().rstrip("/") for link in left.links}
    right_links = {link.casefold().rstrip("/") for link in right.links}
    return bool(left_links & right_links)


def entity_resolution(profiles: list[SocialProfile], threshold: float = 0.5) -> list[EntityMatch]:
    """Score explicit profile signals without asserting identity."""
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("threshold must be between 0 and 1")
    matches: list[EntityMatch] = []
    for left, right in combinations(profiles, 2):
        reasons: list[str] = []
        score = 0.0
        if left.username and right.username and left.username.casefold() == right.username.casefold():
            score += 0.6
            reasons.append("same_username")
        if left.website and right.website and left.website.casefold().rstrip("/") == right.website.casefold().rstrip("/"):
            score += 0.3
            reasons.append("same_website")
        if _shared_links(left, right):
            score += 0.3
            reasons.append("shared_link")
        if left.display_name and right.display_name and left.display_name.casefold() == right.display_name.casefold():
            score += 0.2
            reasons.append("same_display_name")
        if reasons and score >= threshold:
            matches.append(EntityMatch(left.platform, right.platform, min(score, 1.0), tuple(reasons)))
    return matches


def build_evidence_graph(profiles: list[SocialProfile], threshold: float = 0.5) -> list[EvidenceEdge]:
    """Materialize every qualifying explicit signal as a graph edge."""
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("threshold must be between 0 and 1")
    edges: list[EvidenceEdge] = []
    for left, right in combinations(profiles, 2):
        signals = []
        if left.username and right.username and left.username.casefold() == right.username.casefold():
            signals.append(("same_username", 0.6))
        if left.website and right.website and left.website.casefold().rstrip("/") == right.website.casefold().rstrip("/"):
            signals.append(("same_website", 0.3))
        if _shared_links(left, right):
            signals.append(("shared_link", 0.3))
        if left.display_name and right.display_name and left.display_name.casefold() == right.display_name.casefold():
            signals.append(("same_display_name", 0.2))
        total = min(sum(weight for _, weight in signals), 1.0)
        if signals and total >= threshold:
            for signal, weight in signals:
                edges.append(EvidenceEdge(left.platform, left.profile_url, right.platform, right.profile_url, signal, weight))
    return edges
