"""Engine and session factory.

The connection string comes from DATABASE_URL only. Never hardcode it and
never commit one: Railway supplies it in deployment, and local runs point it
at an ephemeral cluster.
"""

from __future__ import annotations

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from backend.config import DATABASE_URL


class DatabaseNotConfigured(RuntimeError):
    """Raised when DATABASE_URL is absent.

    Deliberately loud rather than falling back to SQLite. A silent fallback
    would let migrations and constraint behaviour diverge from Postgres, and
    the schema leans on Postgres enums and CHECK constraints.
    """


def get_engine(url: str | None = None, **kwargs) -> Engine:
    resolved = url or DATABASE_URL
    if not resolved:
        raise DatabaseNotConfigured(
            "DATABASE_URL is not set. Point it at a Postgres instance; "
            "there is no SQLite fallback by design."
        )
    return create_engine(resolved, pool_pre_ping=True, future=True, **kwargs)


def get_sessionmaker(engine: Engine | None = None) -> sessionmaker[Session]:
    return sessionmaker(bind=engine or get_engine(), expire_on_commit=False)


def session_scope(engine: Engine | None = None) -> Iterator[Session]:
    """FastAPI dependency: yields a session, rolls back on error."""
    factory = get_sessionmaker(engine)
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
