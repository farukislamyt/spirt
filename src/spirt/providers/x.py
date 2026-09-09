from spirt.providers.metadata import MetadataProvider, ProviderCapabilities


class XProvider(MetadataProvider):
    def __init__(self) -> None:
        super().__init__(
            name="x",
            capabilities=ProviderCapabilities(
                platform="x",
                hosts=frozenset({"x.com", "www.x.com", "twitter.com", "www.twitter.com"}),
                notes="Public webpage metadata only; authentication and private-data bypass are not supported.",
            ),
        )
