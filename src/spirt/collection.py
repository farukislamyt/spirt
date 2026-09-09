from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class CollectionStatus(StrEnum):
    """Standard outcome of a public-profile collection attempt."""

    SUCCESS = "success"
    PARTIAL = "partial"
    UNAVAILABLE = "unavailable"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class CollectionResult:
    """Structured result for a collection operation."""

    status: CollectionStatus
    data: Any = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "data": self.data.to_dict() if hasattr(self.data, "to_dict") else self.data,
            "error": self.error,
        }
