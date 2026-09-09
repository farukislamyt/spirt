from __future__ import annotations

import json
import re
from html import unescape
from typing import Any

_META_RE = re.compile(
    r'<meta\b[^>]*?(?:property|name)=["\']([^"\']+)["\'][^>]*?content=["\']([^"\']*)["\'][^>]*>',
    re.IGNORECASE,
)
_META_RE_REVERSED = re.compile(
    r'<meta\b[^>]*?content=["\']([^"\']*)["\'][^>]*?(?:property|name)=["\']([^"\']+)["\'][^>]*>',
    re.IGNORECASE,
)


def _clean(value: str) -> str:
    return unescape(re.sub(r"\s+", " ", value)).strip()


def parse_public_metadata(html: str) -> dict[str, Any]:
    """Extract generic OpenGraph/Twitter metadata from supplied HTML."""
    metadata: dict[str, Any] = {}
    for key, value in _META_RE.findall(html):
        normalized = _clean(value)
        if normalized:
            metadata.setdefault(key.lower(), normalized)
    for value, key in _META_RE_REVERSED.findall(html):
        normalized = _clean(value)
        if normalized:
            metadata.setdefault(key.lower(), normalized)

    title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    if title_match:
        title = _clean(title_match.group(1))
        if title:
            metadata.setdefault("title", title)
    return metadata


def parse_json_ld(html: str) -> list[dict[str, Any]]:
    """Extract JSON-LD objects without executing page JavaScript."""
    objects: list[dict[str, Any]] = []
    for raw in re.findall(
        r'<script\b[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
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


def first_json_ld_value(objects: list[dict[str, Any]], key: str) -> str | None:
    """Return the first non-empty scalar value for *key*."""
    for obj in objects:
        value = obj.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None
