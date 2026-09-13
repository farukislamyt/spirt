from __future__ import annotations

import ipaddress
import socket
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener


class FetchError(RuntimeError):
    """Raised when a public resource cannot be fetched safely."""


DEFAULT_TIMEOUT = 10.0
DEFAULT_MAX_BYTES = 2_000_000
DEFAULT_RETRIES = 2
DEFAULT_BACKOFF = 0.25


def _validate_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.netloc:
        raise FetchError("Only absolute HTTPS URLs are supported")
    if parsed.username is not None or parsed.password is not None:
        raise FetchError("URLs containing credentials are not supported")
    try:
        parsed.port
    except ValueError as exc:
        raise FetchError("Invalid URL port") from exc

    host = parsed.hostname
    if not host:
        raise FetchError("URL must contain a hostname")

    try:
        addresses = {
            ipaddress.ip_address(info[4][0])
            for info in socket.getaddrinfo(host, parsed.port or 443, type=socket.SOCK_STREAM)
        }
    except (OSError, ValueError) as exc:
        raise FetchError("Unable to resolve profile host") from exc

    if not addresses or any(not address.is_global for address in addresses):
        raise FetchError("Profile host resolves to a non-public network address")


class _SafeRedirectHandler(HTTPRedirectHandler):
    """Allow redirects only when the destination passes the same URL policy."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        _validate_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _is_retryable_http_error(code: int) -> bool:
    return code == 429 or 500 <= code <= 599


def fetch_text(
    url: str,
    *,
    timeout: float = DEFAULT_TIMEOUT,
    max_bytes: int = DEFAULT_MAX_BYTES,
    retries: int = DEFAULT_RETRIES,
    backoff: float = DEFAULT_BACKOFF,
) -> str:
    """Fetch a bounded public HTTPS document with safe redirects and retries."""
    _validate_url(url)
    if timeout <= 0:
        raise ValueError("timeout must be greater than 0")
    if max_bytes <= 0:
        raise ValueError("max_bytes must be greater than 0")
    if retries < 0:
        raise ValueError("retries must not be negative")
    if backoff < 0:
        raise ValueError("backoff must not be negative")

    request = Request(
        url,
        headers={"User-Agent": "SPIRT/1.0 (+https://github.com/farukislamyt/spirt)"},
        method="GET",
    )
    opener = build_opener(_SafeRedirectHandler)

    for attempt in range(retries + 1):
        try:
            with opener.open(request, timeout=timeout) as response:
                content_type = response.headers.get_content_type()
                if content_type not in {"text/html", "application/xhtml+xml"}:
                    raise FetchError(f"Unsupported content type: {content_type}")

                content_length = response.headers.get("Content-Length")
                if content_length is not None:
                    try:
                        declared_size = int(content_length)
                    except ValueError:
                        declared_size = None
                    if declared_size is not None and declared_size > max_bytes:
                        raise FetchError("Response body exceeds configured size limit")

                body = response.read(max_bytes + 1)
                if len(body) > max_bytes:
                    raise FetchError("Response body exceeds configured size limit")
                return body.decode(response.headers.get_content_charset() or "utf-8", errors="replace")
        except HTTPError as exc:
            if not _is_retryable_http_error(exc.code) or attempt >= retries:
                raise FetchError(f"HTTP {exc.code} while fetching profile") from exc
        except (URLError, TimeoutError) as exc:
            if attempt >= retries:
                raise FetchError("Unable to fetch profile") from exc

        if backoff:
            time.sleep(backoff * (2**attempt))

    raise FetchError("Unable to fetch profile")
