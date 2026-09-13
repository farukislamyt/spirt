import socket
from email.message import Message
from urllib.error import HTTPError

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


@pytest.mark.parametrize("retries", [-1])
def test_fetch_text_rejects_invalid_retries(retries: int) -> None:
    with pytest.raises(ValueError, match="retries"):
        fetch_text("https://example.com/profile", retries=retries)


def test_validate_url_rejects_private_ipv4(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "spirt.http.socket.getaddrinfo",
        lambda *args, **kwargs: [_addr("192.168.1.10")],
    )
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


def test_fetch_text_retries_transient_http_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "spirt.http.socket.getaddrinfo",
        lambda *args, **kwargs: [_addr("93.184.216.34")],
    )
    monkeypatch.setattr("spirt.http.time.sleep", lambda _: None)

    class Response:
        headers = Message()

        def __enter__(self):
            self.headers["Content-Type"] = "text/html; charset=utf-8"
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self, size: int) -> bytes:
            return b"<html>ok</html>"

        def getcode(self):
            return 200

    class Opener:
        def __init__(self):
            self.calls = 0

        def open(self, request, timeout):
            self.calls += 1
            if self.calls < 3:
                raise HTTPError(request.full_url, 503, "temporary", {}, None)
            return Response()

    opener = Opener()
    monkeypatch.setattr("spirt.http.build_opener", lambda handler: opener)
    assert fetch_text("https://example.com/profile", retries=2, backoff=0) == "<html>ok</html>"
    assert opener.calls == 3


def test_fetch_text_does_not_retry_client_http_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "spirt.http.socket.getaddrinfo",
        lambda *args, **kwargs: [_addr("93.184.216.34")],
    )

    class Opener:
        calls = 0

        def open(self, request, timeout):
            self.calls += 1
            raise HTTPError(request.full_url, 404, "not found", {}, None)

    opener = Opener()
    monkeypatch.setattr("spirt.http.build_opener", lambda handler: opener)
    with pytest.raises(FetchError, match="HTTP 404"):
        fetch_text("https://example.com/profile", retries=2, backoff=0)
    assert opener.calls == 1
