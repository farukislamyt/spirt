from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

from spirt.models import SocialProfile


@dataclass(frozen=True, slots=True)
class CorrelationMatch:
    left_platform: str
    right_platform: str
    score: float
    reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {"left_platform": self.left_platform, "right_platform": self.right_platform, "score": self.score, "reasons": list(self.reasons)}


def correlate(profiles: list[SocialProfile], threshold: float = 0.5) -> list[CorrelationMatch]:
    """Find explainable cross-platform similarities; never infer identity from weak signals."""
    matches: list[CorrelationMatch] = []
    for left, right in combinations(profiles, 2):
        reasons: list[str] = []
        score = 0.0
        if left.username and right.username and left.username.casefold() == right.username.casefold():
            score += 0.6
            reasons.append("same_username")
        if left.website and right.website and left.website.casefold() == right.website.casefold():
            score += 0.3
            reasons.append("same_website")
        left_links = {x.casefold().rstrip("/") for x in left.links}
        right_links = {x.casefold().rstrip("/") for x in right.links}
        if left_links & right_links:
            score += 0.3
            reasons.append("shared_link")
        if left.display_name and right.display_name and left.display_name.casefold() == right.display_name.casefold():
            score += 0.2
            reasons.append("same_display_name")
        if reasons and score >= threshold:
            matches.append(CorrelationMatch(left.platform, right.platform, min(score, 1.0), tuple(reasons)))
    return matches
