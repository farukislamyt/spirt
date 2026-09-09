from __future__ import annotations

from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class FetchError(RuntimeError):
    """Raised when a public resource cannot be fetched safely."""


def fetch_text(url: str, *, timeout: float = 10.0) -> str:
    """Fetch a public HTTPS document with a bounded timeout."""
    request = Request(
        url,
        headers={"User-Agent": "SPIRT/0.2 (+https://github.com/farukislamyt/spirt)"},
        method="GET",
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            content_type = response.headers.get_content_type()
            if content_type not in {"text/html", "application/xhtml+xml"}:
                raise FetchError(f"Unsupported content type: {content_type}")
            return response.read().decode(response.headers.get_content_charset() or "utf-8", errors="replace")
    except HTTPError as exc:
        raise FetchError(f"HTTP {exc.code} while fetching profile") from exc
    except (URLError, TimeoutError) as exc:
        raise FetchError("Unable to fetch profile") from exc
