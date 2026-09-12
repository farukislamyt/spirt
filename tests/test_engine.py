from __future__ import annotations

import time

import pytest

from spirt.collection import CollectionErrorCode, CollectionResult, CollectionStatus
from spirt.engine import CollectionCache, ProviderHealthTracker, collect_many, collect_many_async
from spirt.models import SocialProfile
from spirt.providers import Provider


class FakeProvider(Provider):
    name = "fake"

    def __init__(self, *, delay: float = 0.0, fail: bool = False) -> None:
        self.delay = delay
        self.fail = fail
        self.calls = 0

    def supports(self, url: str) -> bool:
        return url.startswith("https://example.test/")

    def collect(self, url: str) -> CollectionResult:
        self.calls += 1
        if self.delay:
            time.sleep(self.delay)
        if self.fail:
            raise RuntimeError("boom")
        return CollectionResult(CollectionStatus.SUCCESS, SocialProfile(platform=self.name, profile_url=url))


def test_collect_many_deduplicates_and_preserves_order() -> None:
    provider = FakeProvider()
    urls = ["https://example.test/a", "https://example.test/b", "https://example.test/a"]

    results = collect_many(urls, providers=[provider])

    assert [result.data.profile_url for result in results] == [
        "https://example.test/a",
        "https://example.test/b",
    ]
    assert provider.calls == 2


def test_collect_many_isolates_provider_failure() -> None:
    provider = FakeProvider(fail=True)
    results = collect_many(["https://example.test/a"], providers=[provider])

    assert results[0].status is CollectionStatus.FAILED
    assert results[0].error_code is CollectionErrorCode.UNKNOWN


def test_collect_many_concurrency_reduces_wall_time() -> None:
    provider = FakeProvider(delay=0.08)
    urls = [f"https://example.test/{i}" for i in range(4)]

    started = time.monotonic()
    results = collect_many(urls, providers=[provider], max_concurrency=4)
    elapsed = time.monotonic() - started

    assert len(results) == 4
    assert elapsed < 0.24


@pytest.mark.asyncio
async def test_async_engine_uses_cache() -> None:
    provider = FakeProvider()
    cache = CollectionCache(ttl=60)

    first = await collect_many_async(["https://example.test/a"], providers=[provider], cache=cache)
    second = await collect_many_async(["https://example.test/a"], providers=[provider], cache=cache)

    assert first[0].status is CollectionStatus.SUCCESS
    assert second[0].status is CollectionStatus.SUCCESS
    assert provider.calls == 1


def test_provider_health_tracks_outcomes() -> None:
    provider = FakeProvider()
    health = ProviderHealthTracker([provider])

    collect_many(["https://example.test/a"], providers=[provider], health=health)
    snapshot = health.snapshot()

    assert snapshot[0].provider == "fake"
    assert snapshot[0].successes == 1
    assert snapshot[0].total == 1
