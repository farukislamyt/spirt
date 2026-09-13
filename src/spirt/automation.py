from __future__ import annotations

from collections.abc import Iterable, Sequence

from spirt.collection import CollectionResult
from spirt.engine import CollectionCache, ProviderHealthTracker, collect_many as _collect_many
from spirt.providers import Provider


def collect_many(
    urls: Iterable[str],
    *,
    providers: Sequence[Provider] | None = None,
    max_concurrency: int = 8,
    cache: CollectionCache | None = None,
    health: ProviderHealthTracker | None = None,
) -> list[CollectionResult]:
    """Collect a deterministic batch using the concurrent collection engine."""
    return _collect_many(
        urls,
        providers=providers,
        max_concurrency=max_concurrency,
        cache=cache,
        health=health,
    )
