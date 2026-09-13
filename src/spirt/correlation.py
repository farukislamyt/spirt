from __future__ import annotations

from spirt.intelligence import EntityMatch, entity_resolution
from spirt.models import SocialProfile

CorrelationMatch = EntityMatch


def correlate(profiles: list[SocialProfile], threshold: float = 0.5) -> list[CorrelationMatch]:
    """Find explainable cross-platform similarities without asserting identity."""
    return entity_resolution(profiles, threshold=threshold)
