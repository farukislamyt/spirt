from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class Evidence:
    """Provenance for a normalized value collected from a public source."""

    field: str
    value: str
    source_url: str
    source_type: str = "public_webpage"
    method: str = "metadata"
    confidence: float = 1.0

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")

    def to_dict(self) -> dict[str, Any]:
        return {
            "field": self.field,
            "value": self.value,
            "source_url": self.source_url,
            "source_type": self.source_type,
            "method": self.method,
            "confidence": self.confidence,
        }
