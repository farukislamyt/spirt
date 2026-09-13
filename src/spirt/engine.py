from __future__ import annotations

import asyncio
import time
from collections import Counter
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from threading import Lock
from typing import Any

from spirt.collection import CollectionErrorCode, CollectionResult, CollectionStatus
from spirt.providers import Provider
from spirt.providers.registry import get_provider, list_providers


@dataclass(frozen=True, slots=True)
class ProviderHealth:
    """A read-only snapshot of collection outcomes for one provider."""

    provider: str
    successes: int = 0
    partials: int = 0
    unavailable: int = 0
    failures: int = 0

    @property
    def total(self) -> int:
        return self.successes + self.partials + self.unavailable + self.failures

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "successes": self.successes,
            "partials": self.partials,
            "unavailable": self.unavailable,
            "failures": self.failures,
            "total": self.total,
        }


class ProviderHealthTracker:
    """Thread-safe provider outcome counters for batch collection."""

    def __init__(self, providers: Iterable[Provider] = ()) -> None:
        self._lock = Lock()
        self._counts: Counter[str] = Counter()
        for provider in providers:
            self._counts[provider.name] += 0

    def record(self, provider: Provider, result: CollectionResult) -> None:
        key = {
            CollectionStatus.SUCCESS: "successes",
            CollectionStatus.PARTIAL: "partials",
            CollectionStatus.UNAVAILABLE: "unavailable",
            CollectionStatus.FAILED: "failures",
        }[result.status]
        with self._lock:
            self._counts[f"{provider.name}:{key}"] += 1

    def snapshot(self) -> tuple[ProviderHealth, ...]:
        with self._lock:
            names = sorted({key.split(":", 1)[0] for key in self._counts})
            return tuple(
                ProviderHealth(
                    provider=name,
                    successes=self._counts[f"{name}:successes"],
                    partials=self._counts[f"{name}:partials"],
                    unavailable=self._counts[f"{name}:unavailable"],
                    failures=self._counts[f"{name}:failures"],
                )
                for name in names
            )


@dataclass(frozen=True, slots=True)
class _CacheEntry:
    expires_at: float
    result: CollectionResult


class CollectionCache:
    """Small in-memory TTL cache for public collection results."""

    def __init__(self, ttl: float = 300.0) -> None:
        if ttl < 0:
            raise ValueError("ttl must be non-negative")
        self.ttl = ttl
        self._lock = Lock()
        self._items: dict[str, _CacheEntry] = {}

    def get(self, key: str) -> CollectionResult | None:
        now = time.monotonic()
        with self._lock:
            entry = self._items.get(key)
            if entry is None:
                return None
            if entry.expires_at <= now:
                del self._items[key]
                return None
            return entry.result

    def put(self, key: str, result: CollectionResult) -> None:
        if self.ttl == 0:
            return
        with self._lock:
            self._items[key] = _CacheEntry(time.monotonic() + self.ttl, result)

    def clear(self) -> None:
        with self._lock:
            self._items.clear()


def _cache_key(url: str) -> str:
    return url.strip()


def _failed(message: str) -> CollectionResult:
    return CollectionResult(
        status=CollectionStatus.FAILED,
        error=message,
        error_code=CollectionErrorCode.UNKNOWN,
    )


def collect_one(
    url: str,
    *,
    providers: Sequence[Provider] | None = None,
    cache: CollectionCache | None = None,
    health: ProviderHealthTracker | None = None,
) -> CollectionResult:
    """Collect one URL with graceful error isolation, caching, and health tracking."""
    key = _cache_key(url)
    if cache is not None:
        cached = cache.get(key)
        if cached is not None:
            return cached
    try:
        provider = _get_provider(url, providers)
        result = provider.collect(url)
    except ValueError as exc:
        return _failed(str(exc))
    except Exception as exc:  # provider failures must not abort a batch
        result = _failed(f"Provider collection failed: {exc}")
        if health is not None:
            health.record(provider, result) if "provider" in locals() else None
        return result
    if health is not None:
        health.record(provider, result)
    if cache is not None:
        cache.put(key, result)
    return result


def _get_provider(url: str, providers: Sequence[Provider] | None) -> Provider:
    if providers is None:
        return get_provider(url)
    for provider in providers:
        if provider.supports(url):
            return provider
    raise ValueError("No SPIRT provider supports this URL")


async def collect_many_async(
    urls: Iterable[str],
    *,
    providers: Sequence[Provider] | None = None,
    max_concurrency: int = 8,
    cache: CollectionCache | None = None,
    health: ProviderHealthTracker | None = None,
) -> list[CollectionResult]:
    """Collect a batch concurrently while preserving input order and isolating failures.

    Provider implementations remain synchronous today, so each collection runs in
    a worker thread via ``asyncio.to_thread``. This provides concurrent orchestration
    without introducing a new HTTP client dependency or changing provider contracts.
    """
    if max_concurrency < 1:
        raise ValueError("max_concurrency must be at least 1")
    unique_urls = list(dict.fromkeys(urls))
    semaphore = asyncio.Semaphore(max_concurrency)

    async def run(url: str) -> CollectionResult:
        async with semaphore:
            return await asyncio.to_thread(
                collect_one,
                url,
                providers=providers,
                cache=cache,
                health=health,
            )

    return list(await asyncio.gather(*(run(url) for url in unique_urls)))


def collect_many(
    urls: Iterable[str],
    *,
    providers: Sequence[Provider] | None = None,
    max_concurrency: int = 8,
    cache: CollectionCache | None = None,
    health: ProviderHealthTracker | None = None,
) -> list[CollectionResult]:
    """Synchronous compatibility wrapper around the concurrent collection engine."""
    return asyncio.run(
        collect_many_async(
            urls,
            providers=providers,
            max_concurrency=max_concurrency,
            cache=cache,
            health=health,
        )
    )
