from __future__ import annotations

from spirt.providers import Provider
from spirt.providers.facebook import FacebookProvider


_PROVIDERS: tuple[Provider, ...] = (FacebookProvider(),)


def get_provider(url: str) -> Provider:
    """Return the first provider that supports the URL."""
    for provider in _PROVIDERS:
        if provider.supports(url):
            return provider
    raise ValueError(f"No provider supports URL: {url}")
