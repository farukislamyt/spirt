from __future__ import annotations

import re
from urllib.parse import urlparse

SUPPORTED_HOSTS = {
    "facebook.com": "facebook", "www.facebook.com": "facebook", "m.facebook.com": "facebook", "mbasic.facebook.com": "facebook",
    "instagram.com": "instagram", "www.instagram.com": "instagram",
    "linkedin.com": "linkedin", "www.linkedin.com": "linkedin",
    "x.com": "x", "www.x.com": "x", "twitter.com": "x", "www.twitter.com": "x",
    "tiktok.com": "tiktok", "www.tiktok.com": "tiktok",
    "github.com": "github", "www.github.com": "github",
}
_URL_RE = re.compile(r"https://[^\s<>\"']+")


def discover_urls(text: str) -> list[str]:
    """Extract supported HTTPS profile URLs from text without contacting them."""
    found: list[str] = []
    seen: set[str] = set()
    for raw in _URL_RE.findall(text):
        url = raw.rstrip(".,;:!?)]}")
        parsed = urlparse(url)
        if parsed.hostname not in SUPPORTED_HOSTS or url in seen:
            continue
        seen.add(url)
        found.append(url)
    return found


def discover_profiles(text: str) -> list[dict[str, str]]:
    return [
        {"platform": SUPPORTED_HOSTS[urlparse(url).hostname], "url": url}
        for url in discover_urls(text)
    ]
