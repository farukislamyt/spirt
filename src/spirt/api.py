from __future__ import annotations

from spirt.providers.registry import get_provider


def create_app():
    """Create the optional FastAPI application. Requires `spirt[api]`."""
    try:
        from fastapi import FastAPI, HTTPException
    except ImportError as exc:
        raise RuntimeError("Install the API extra with `pip install 'spirt[api]'`.") from exc

    app = FastAPI(title="SPIRT API", version="0.9.0")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "spirt"}

    @app.get("/v1/profile")
    def profile(url: str) -> dict[str, object]:
        try:
            result = get_provider(url).collect(url)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return result.to_dict()

    return app


app = None
