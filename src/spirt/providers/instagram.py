from spirt.providers.metadata import MetadataProvider, ProviderCapabilities


class InstagramProvider(MetadataProvider):
    def __init__(self) -> None:
        super().__init__(
            name="instagram",
            capabilities=ProviderCapabilities(
                platform="instagram",
                hosts=frozenset({"instagram.com", "www.instagram.com"}),
                notes="Public webpage metadata only; private-profile or access-control bypass is not supported.",
            ),
        )
