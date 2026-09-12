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
    """Structured result for a collection operation.

    A successful result must contain collected data. Failed and unavailable
    results must explain the failure so callers can distinguish an empty
    result from an unsuccessful collection attempt.
    """

    status: CollectionStatus
    data: Any = None
    error: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.status, CollectionStatus):
            raise TypeError("status must be a CollectionStatus")

        if self.status is CollectionStatus.SUCCESS and self.data is None:
            raise ValueError("successful collection results must contain data")

        if self.status in {CollectionStatus.UNAVAILABLE, CollectionStatus.FAILED}:
            if self.error is None or not self.error.strip():
                raise ValueError(f"{self.status.value} collection results must contain an error")

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "data": self.data.to_dict() if hasattr(self.data, "to_dict") else self.data,
            "error": self.error,
        }
