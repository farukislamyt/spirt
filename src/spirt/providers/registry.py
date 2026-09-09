from __future__ import annotations

from spirt.providers import Provider
from spirt.providers.facebook import FacebookProvider
from spirt.providers.github import GitHubProvider
from spirt.providers.instagram import InstagramProvider
from spirt.providers.linkedin import LinkedInProvider
from spirt.providers.tiktok import TikTokProvider
from spirt.providers.x import XProvider

_PROVIDERS: tuple[Provider, ...] = (
    FacebookProvider(),
    InstagramProvider(),
    LinkedInProvider(),
    XProvider(),
    TikTokProvider(),
    GitHubProvider(),
)


def get_provider(url: str) -> Provider:
    for provider in _PROVIDERS:
        if provider.supports(url):
            return provider
    raise ValueError("No SPIRT provider supports this URL")


def list_providers() -> tuple[Provider, ...]:
    return _PROVIDERS
