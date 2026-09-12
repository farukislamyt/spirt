from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse


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
        if not self.field.strip():
            raise ValueError("field must not be empty")
        if not self.source_url.strip():
            raise ValueError("source_url must not be empty")
        parsed = urlparse(self.source_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("source_url must be an absolute HTTP(S) URL")
        if not self.source_type.strip():
            raise ValueError("source_type must not be empty")
        if not self.method.strip():
            raise ValueError("method must not be empty")
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
