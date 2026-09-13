from __future__ import annotations

from typing import Any

from spirt import __version__
from spirt.automation import collect_many
from spirt.providers.registry import get_provider, list_providers
from spirt.reporting import render_report_html, render_report_json, render_report_markdown


def create_app():
    """Create the optional FastAPI application. Requires `spirt[api]`."""
    try:
        from fastapi import FastAPI, HTTPException, Query
    except ImportError as exc:
        raise RuntimeError("Install the API extra with `pip install 'spirt[api]'`.") from exc

    app = FastAPI(title="SPIRT API", version=__version__, description="Public-profile OSINT collection API.")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "spirt", "version": __version__}

    @app.get("/v1/providers")
    def providers() -> list[dict[str, Any]]:
        return [
            {"name": provider.name, "hosts": sorted(getattr(getattr(provider, "capabilities", None), "hosts", []))}
            for provider in list_providers()
        ]

    @app.get("/v1/profile")
    def profile(url: str = Query(..., min_length=1, max_length=2048)) -> dict[str, object]:
        try:
            result = get_provider(url).collect(url)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return result.to_dict()

    @app.post("/v1/report")
    def report(urls: list[str], format: str = Query("json", pattern="^(json|markdown|html)$")) -> dict[str, str]:
        if not urls or len(urls) > 100:
            raise HTTPException(status_code=400, detail="urls must contain between 1 and 100 items")
        if any(not isinstance(url, str) or not url.strip() or len(url) > 2048 for url in urls):
            raise HTTPException(status_code=400, detail="each URL must be a non-empty string of at most 2048 characters")
        results = collect_many(urls)
        content = {
            "json": render_report_json(results),
            "markdown": render_report_markdown(results),
            "html": render_report_html(results),
        }[format]
        return {"format": format, "content": content}

    return app


app = None
