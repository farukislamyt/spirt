from spirt.providers.metadata import MetadataProvider, ProviderCapabilities


class GitHubProvider(MetadataProvider):
    def __init__(self) -> None:
        super().__init__(
            name="github",
            capabilities=ProviderCapabilities(
                platform="github",
                hosts=frozenset({"github.com", "www.github.com"}),
                notes="Public webpage metadata only; authenticated API access can be added as a separate authorized adapter.",
            ),
        )
