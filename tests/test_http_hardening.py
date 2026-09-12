import socket

import pytest

from spirt.http import FetchError, _SafeRedirectHandler, _validate_url, fetch_text


def _addr(ip: str) -> tuple[int, int, int, str, tuple[str, int]]:
    return (socket.AF_INET6 if ":" in ip else socket.AF_INET, socket.SOCK_STREAM, 6, "", (ip, 443))


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


def test_validate_url_rejects_private_ipv4(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("spirt.http.socket.getaddrinfo", lambda *args, **kwargs: [_addr("192.168.1.10")])
    with pytest.raises(FetchError, match="non-public"):
        _validate_url("https://internal.example/profile")


def test_validate_url_rejects_loopback_ipv6(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("spirt.http.socket.getaddrinfo", lambda *args, **kwargs: [_addr("::1")])
    with pytest.raises(FetchError, match="non-public"):
        _validate_url("https://internal.example/profile")


def test_validate_url_rejects_mixed_public_and_private_dns(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "spirt.http.socket.getaddrinfo",
        lambda *args, **kwargs: [_addr("93.184.216.34"), _addr("10.0.0.5")],
    )
    with pytest.raises(FetchError, match="non-public"):
        _validate_url("https://example.com/profile")


def test_validate_url_rejects_credentials() -> None:
    with pytest.raises(FetchError, match="credentials"):
        _validate_url("https://user:password@example.com/profile")


def test_redirect_handler_rejects_http_destination(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("spirt.http.socket.getaddrinfo", lambda *args, **kwargs: [_addr("93.184.216.34")])
    handler = _SafeRedirectHandler()
    with pytest.raises(FetchError, match="HTTPS"):
        handler.redirect_request(
            type("Request", (), {})(),
            None,
            302,
            "Found",
            {},
            "http://example.com/private",
        )
