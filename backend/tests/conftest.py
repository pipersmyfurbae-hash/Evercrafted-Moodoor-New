"""Shared pytest fixtures.

Database tests need a real Postgres. They skip rather than fail when
DATABASE_URL is unset, so the schema-independent suite -- including all
three drift tripwires -- still runs anywhere.
"""

from __future__ import annotations

import os

import pytest
from sqlalchemy import text

from backend.db.base import Base


@pytest.fixture(scope="session")
def database_url() -> str:
    url = os.environ.get("DATABASE_URL", "")
    if not url:
        pytest.skip("DATABASE_URL not set; skipping database-backed tests")
    return url


@pytest.fixture(scope="session")
def engine(database_url: str):
    from backend.db.session import get_engine

    eng = get_engine(database_url)
    with eng.connect() as conn:
        conn.execute(text("SELECT 1"))
    return eng


@pytest.fixture()
def db_session(engine):
    """A session wrapped in a transaction that is always rolled back.

    Tests never leave rows behind, so ordering between them cannot become a
    hidden dependency.
    """
    from sqlalchemy.orm import Session

    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, expire_on_commit=False)
    try:
        yield session
    finally:
        session.close()
        # A test that provoked an IntegrityError has already had its
        # transaction rolled back by the driver, so only roll back one that
        # is still live.
        if transaction.is_active:
            transaction.rollback()
        connection.close()


@pytest.fixture(scope="session")
def created_schema(engine):
    """Create tables directly from metadata.

    Used only by tests that need tables present. Migration correctness is
    tested separately, by running Alembic itself.
    """
    Base.metadata.create_all(engine)
    return engine
