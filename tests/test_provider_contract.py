from spirt.collection import CollectionResult, CollectionStatus
from spirt.models import SocialProfile
from spirt.providers import Provider


class FakeProvider(Provider):
    name = "fake"

    def supports(self, url: str) -> bool:
        return url.startswith("https://fake.example/")

    def collect(self, url: str) -> CollectionResult:
        return CollectionResult(CollectionStatus.SUCCESS, SocialProfile(platform=self.name, profile_url=url))


def test_provider_contract_is_platform_agnostic() -> None:
    provider = FakeProvider()
    assert provider.supports("https://fake.example/alice")
    result = provider.collect("https://fake.example/alice")
    assert result.status is CollectionStatus.SUCCESS
    assert result.data.platform == "fake"
