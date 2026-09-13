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


class CollectionErrorCode(StrEnum):
    """Machine-readable reason for an unsuccessful collection."""

    UNSUPPORTED_URL = "unsupported_url"
    NETWORK_UNAVAILABLE = "network_unavailable"
    INVALID_RESPONSE = "invalid_response"
    PARSE_ERROR = "parse_error"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class CollectionResult:
    """Structured result for a collection operation."""

    status: CollectionStatus
    data: Any = None
    error: str | None = None
    error_code: CollectionErrorCode | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.status, CollectionStatus):
            raise TypeError("status must be a CollectionStatus")
        if self.error_code is not None and not isinstance(self.error_code, CollectionErrorCode):
            raise TypeError("error_code must be a CollectionErrorCode or None")
        if self.status is CollectionStatus.SUCCESS:
            if self.data is None:
                raise ValueError("successful collection results must contain data")
            if self.error is not None or self.error_code is not None:
                raise ValueError("successful collection results cannot contain an error")
        elif self.status is CollectionStatus.PARTIAL:
            if self.data is None and not self.error:
                raise ValueError("partial collection results must contain data or an error")
            if self.error is not None and self.error_code is None:
                raise ValueError("partial collection errors must include an error_code")
        elif self.status in {CollectionStatus.UNAVAILABLE, CollectionStatus.FAILED}:
            if self.error is None or not self.error.strip():
                raise ValueError(f"{self.status.value} collection results must contain an error")
            if self.error_code is None:
                raise ValueError(f"{self.status.value} collection results must include an error_code")

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "data": self.data.to_dict() if hasattr(self.data, "to_dict") else self.data,
            "error": self.error,
            "error_code": self.error_code.value if self.error_code else None,
        }
