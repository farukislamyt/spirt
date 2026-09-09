from __future__ import annotations

from collections.abc import Iterable

from spirt.collection import CollectionResult, CollectionStatus
from spirt.providers.registry import get_provider


def collect_many(urls: Iterable[str]) -> list[CollectionResult]:
    """Collect a deterministic batch without bypassing provider access controls."""
    results: list[CollectionResult] = []
    for url in dict.fromkeys(urls):
        try:
            results.append(get_provider(url).collect(url))
        except ValueError as exc:
            results.append(CollectionResult(CollectionStatus.FAILED, error=str(exc)))
    return results
