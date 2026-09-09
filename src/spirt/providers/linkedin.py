from spirt.providers.metadata import MetadataProvider, ProviderCapabilities


class LinkedInProvider(MetadataProvider):
    def __init__(self) -> None:
        super().__init__(
            name="linkedin",
            capabilities=ProviderCapabilities(
                platform="linkedin",
                hosts=frozenset({"linkedin.com", "www.linkedin.com"}),
                notes="Public webpage metadata only; authentication and private-data bypass are not supported.",
            ),
        )
