from spirt.providers.metadata import MetadataProvider, ProviderCapabilities


class TikTokProvider(MetadataProvider):
    def __init__(self) -> None:
        super().__init__(
            name="tiktok",
            capabilities=ProviderCapabilities(
                platform="tiktok",
                hosts=frozenset({"tiktok.com", "www.tiktok.com"}),
                notes="Public webpage metadata only; authentication and private-data bypass are not supported.",
            ),
        )
