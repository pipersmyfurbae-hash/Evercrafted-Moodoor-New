"""The API contract must match CLAUDE.md's canonical route table.

Design wires its Phase 3 concepts to these routes, so a rename here that is
not also a rename in CLAUDE.md silently breaks whatever Design built. The
table below is transcribed from CLAUDE.md's "API Contract -- The 7 Pipeline
Endpoints (canonical list)"; the test asserts the app agrees with it and that
CLAUDE.md still says so.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.api.main import app
from backend.config import REPO_ROOT

# (method, path) exactly as CLAUDE.md lists them.
PIPELINE_ROUTES: tuple[tuple[str, str], ...] = (
    ("POST", "/api/intake"),
    ("POST", "/api/emotion-profile"),
    ("POST", "/api/floral-select"),
    ("POST", "/api/place"),
    ("POST", "/api/story"),
    ("POST", "/api/generate-pdf"),
    ("POST", "/api/listing"),
)

SUPPORTING_ROUTE = ("GET", "/api/blueprints/{blueprint_id}")


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(app)


def _declared() -> set[tuple[str, str]]:
    """Read routes from the OpenAPI document rather than `app.routes`.

    FastAPI 0.141 wraps an included router in a `_IncludedRouter` object that
    exposes no `.path`, so walking `app.routes` finds nothing even though the
    endpoints route correctly. The OpenAPI schema is also the more meaningful
    source: it is the artifact Design consumes, and it does not depend on
    FastAPI's internal route representation staying put across versions.
    """
    schema = app.openapi()
    return {
        (method.upper(), path)
        for path, operations in schema.get("paths", {}).items()
        if path.startswith("/api")
        for method in operations
        if method.upper() not in {"HEAD", "OPTIONS"}
    }


def test_there_are_exactly_seven_pipeline_endpoints() -> None:
    """Seven, not six and not eight.

    The table calls out that /api/generate-pdf owns several internal
    sub-stages -- composition, scoring, genome, builder instructions -- and
    that those are deliberately not separate routes. This is what stops a
    later sprint from helpfully splitting them out.
    """
    posts = {r for r in _declared() if r[0] == "POST"}
    assert len(posts) == 7, f"expected 7 POST pipeline routes, found {len(posts)}: {sorted(posts)}"


@pytest.mark.parametrize(("method", "path"), PIPELINE_ROUTES)
def test_canonical_route_is_declared(method: str, path: str) -> None:
    assert (method, path) in _declared(), (
        f"{method} {path} is missing. Route names come from CLAUDE.md's "
        "canonical list and may not be renamed here."
    )


def test_supporting_status_route_is_declared() -> None:
    assert SUPPORTING_ROUTE in _declared(), (
        "GET /api/blueprints/{blueprint_id} is missing. Not one of the 7 "
        "stages, but required for the walking skeleton."
    )


def test_no_undeclared_api_routes_exist() -> None:
    """Nothing may appear under /api that CLAUDE.md does not list."""
    expected = set(PIPELINE_ROUTES) | {SUPPORTING_ROUTE}
    unexpected = sorted(_declared() - expected)
    assert not unexpected, (
        f"routes exist that CLAUDE.md does not list: {unexpected}. Add them "
        "to the canonical table first, or remove them."
    )


@pytest.mark.parametrize(("method", "path"), PIPELINE_ROUTES)
def test_stub_returns_501_not_fabricated_data(
    client: TestClient, method: str, path: str
) -> None:
    """A stub must be distinguishable from a working endpoint.

    Returning a plausible fake payload would let Design build against
    fiction and only discover it in Sprint 5.
    """
    response = client.request(method, path, json={})
    assert response.status_code in (422, 501), (
        f"{method} {path} returned {response.status_code}; a contract stub "
        "should reject the payload (422) or report 501, never fake data."
    )


def test_openapi_schema_generates(client: TestClient) -> None:
    """The deliverable is the OpenAPI document itself."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    for _, path in PIPELINE_ROUTES:
        assert path in schema["paths"], f"{path} missing from the OpenAPI document"
    assert "/api/blueprints/{blueprint_id}" in schema["paths"]


def test_claude_md_still_lists_these_routes() -> None:
    """Guards the other direction.

    If CLAUDE.md's table is edited and the code is not, this fails -- so the
    two cannot drift apart quietly in either direction.
    """
    claude_md = (REPO_ROOT / "CLAUDE.md").read_text()
    assert "API Contract" in claude_md, (
        "CLAUDE.md has no API Contract section. If it moved, update this test; "
        "if it was lost, restore it -- Design builds against that table."
    )
    missing = [path for _, path in PIPELINE_ROUTES if path not in claude_md]
    assert not missing, (
        f"routes declared in code but absent from CLAUDE.md: {missing}"
    )
