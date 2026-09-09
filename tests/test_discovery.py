from spirt.discovery import discover_profiles


def test_discovery_finds_supported_urls_and_deduplicates() -> None:
    text = "See https://github.com/alice and https://www.instagram.com/alice. See https://github.com/alice again."
    assert discover_profiles(text) == [
        {"platform": "github", "url": "https://github.com/alice"},
        {"platform": "instagram", "url": "https://www.instagram.com/alice"},
    ]
