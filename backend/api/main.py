"""FastAPI application.

STATUS: the 7 pipeline endpoints are NOT defined here yet, and their absence
is deliberate.

Sprint 0's definition-of-done calls for an OpenAPI contract stub covering the
7 pipeline endpoints plus GET /api/blueprints/{id}. The canonical route table
lives in CLAUDE.md under "API Contract -- The 7 Pipeline Endpoints", which has
not yet reached this repository -- origin/main still carries the older
CLAUDE.md with no such section.

Design wires its Phase 3 concepts to whatever contract lands here, so guessing
at route names, payload shapes, or status codes would produce something for
Design to build against and later discover was invented. The routes go in when
the table arrives; nothing else in Sprint 0 depends on them.

What exists now: the app object, health checks, and the error contract, so the
service is deployable and Railway has something to probe.
"""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from backend.config import BLUEPRINT_SCHEMA_VERSION

app = FastAPI(
    title="Evercrafted Empathy Engine",
    description=(
        "Turns a customer's emotional input into a deterministic, sellable "
        "wreath blueprint."
    ),
    version="0.1.0",
)


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
