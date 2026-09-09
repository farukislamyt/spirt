from __future__ import annotations

import json
import re
from html import unescape
from typing import Any


_META_RE = re.compile(
    r'<meta[^>]+(?:property|name)=["\']([^"\']+)["\'][^>]+content=["\']([^"\']*)["\'][^>]*>',
    re.IGNORECASE,
)


def parse_public_metadata(html: str) -> dict[str, Any]:
    """Extract generic OpenGraph/Twitter metadata from supplied HTML."""
    metadata: dict[str, Any] = {}
    for key, value in _META_RE.findall(html):
        normalized = unescape(value).strip()
        if normalized:
            metadata.setdefault(key.lower(), normalized)

    title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    if title_match:
        metadata.setdefault("title", unescape(re.sub(r"\s+", " ", title_match.group(1))).strip())

    return metadata


def parse_json_ld(html: str) -> list[dict[str, Any]]:
    """Extract JSON-LD objects without executing page JavaScript."""
    objects: list[dict[str, Any]] = []
    for raw in re.findall(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html,
        re.IGNORECASE | re.DOTALL,
    ):
        try:
            data = json.loads(raw.strip())
        except json.JSONDecodeError:
            continue
        values = data if isinstance(data, list) else [data]
        objects.extend(item for item in values if isinstance(item, dict))
    return objects
