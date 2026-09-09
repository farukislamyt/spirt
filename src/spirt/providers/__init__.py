from __future__ import annotations

from abc import ABC, abstractmethod

from spirt.collection import CollectionResult


class Provider(ABC):
    """Interface implemented by social-profile providers."""

    name: str

    @abstractmethod
    def supports(self, url: str) -> bool:
        """Return whether this provider can handle the supplied URL."""

    @abstractmethod
    def collect(self, url: str) -> CollectionResult:
        """Collect publicly available information from a supported profile."""


__all__ = ["Provider"]
