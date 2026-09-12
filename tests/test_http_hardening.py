import pytest

from spirt.http import FetchError, fetch_text


def test_fetch_text_rejects_non_https_before_network_access() -> None:
    with pytest.raises(FetchError, match="HTTPS"):
        fetch_text("http://example.com/profile")


def test_fetch_text_rejects_invalid_url_before_network_access() -> None:
    with pytest.raises(FetchError, match="HTTPS"):
        fetch_text("not-a-url")


@pytest.mark.parametrize("timeout", [0, -1])
def test_fetch_text_rejects_invalid_timeout(timeout: float) -> None:
    with pytest.raises(ValueError, match="timeout"):
        fetch_text("https://example.com/profile", timeout=timeout)


@pytest.mark.parametrize("max_bytes", [0, -1])
def test_fetch_text_rejects_invalid_size_limit(max_bytes: int) -> None:
    with pytest.raises(ValueError, match="max_bytes"):
        fetch_text("https://example.com/profile", max_bytes=max_bytes)
