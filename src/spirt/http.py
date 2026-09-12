from __future__ import annotations

from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


class FetchError(RuntimeError):
    """Raised when a public resource cannot be fetched safely."""


DEFAULT_TIMEOUT = 10.0
DEFAULT_MAX_BYTES = 2_000_000


def _validate_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.netloc:
        raise FetchError("Only absolute HTTPS URLs are supported")


def fetch_text(
    url: str,
    *,
    timeout: float = DEFAULT_TIMEOUT,
    max_bytes: int = DEFAULT_MAX_BYTES,
) -> str:
    """Fetch a bounded public HTTPS document with a bounded timeout."""
    _validate_url(url)
    if timeout <= 0:
        raise ValueError("timeout must be greater than 0")
    if max_bytes <= 0:
        raise ValueError("max_bytes must be greater than 0")

    request = Request(
        url,
        headers={"User-Agent": "SPIRT/1.0 (+https://github.com/farukislamyt/spirt)"},
        method="GET",
    )
    try:
        with urlopen(request, timeout=timeout) as response:
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
        raise FetchError(f"HTTP {exc.code} while fetching profile") from exc
    except (URLError, TimeoutError) as exc:
        raise FetchError("Unable to fetch profile") from exc
