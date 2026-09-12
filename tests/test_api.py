import pytest

from spirt.api import create_app


def test_api_requires_optional_dependency_or_builds_app() -> None:
    try:
        app = create_app()
    except RuntimeError as exc:
        assert "spirt[api]" in str(exc)
        return
    assert app.title == "SPIRT API"
    routes = {route.path for route in app.routes}
    assert {"/health", "/v1/providers", "/v1/profile", "/v1/report"} <= routes
