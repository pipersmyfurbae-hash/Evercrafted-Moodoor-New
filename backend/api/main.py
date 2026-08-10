"""FastAPI application.

The 7 pipeline endpoints plus GET /api/blueprints/{id} are declared in
`routes.py` as a contract stub: real request and response shapes, no bodies.
Route names are transcribed from CLAUDE.md's "API Contract -- The 7 Pipeline
Endpoints (canonical list)" and must not be renamed here.

Design wires its Phase 3 concepts to this contract, so the shapes are the
Sprint 0 deliverable. Every stub returns 501 rather than fabricated data --
a client that receives plausible fake output cannot tell a stub from a
working endpoint.
"""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from backend.api.routes import router as pipeline_router
from backend.config import BLUEPRINT_SCHEMA_VERSION

app = FastAPI(
    title="Evercrafted Empathy Engine",
    description=(
        "Turns a customer's emotional input into a deterministic, sellable "
        "wreath blueprint."
    ),
    version="0.1.0",
)

app.include_router(pipeline_router)


class HealthResponse(BaseModel):
    status: str
    blueprint_schema_version: str


class ReadinessResponse(BaseModel):
    status: str
    database: str


@app.get("/health", response_model=HealthResponse, tags=["ops"])
def health() -> HealthResponse:
    """Liveness. Deliberately touches nothing external."""
    return HealthResponse(
        status="ok", blueprint_schema_version=BLUEPRINT_SCHEMA_VERSION
    )


@app.get("/ready", response_model=ReadinessResponse, tags=["ops"])
def ready() -> ReadinessResponse:
    """Readiness: reports whether the database is reachable.

    Returns 200 with a degraded body rather than raising, so a probe can
    distinguish "process up, database down" from "process down".
    """
    from sqlalchemy import text

    from backend.db.session import DatabaseNotConfigured, get_engine

    try:
        with get_engine().connect() as conn:
            conn.execute(text("SELECT 1"))
    except DatabaseNotConfigured:
        return ReadinessResponse(status="degraded", database="not_configured")
    except Exception:
        return ReadinessResponse(status="degraded", database="unreachable")
    return ReadinessResponse(status="ok", database="ok")
