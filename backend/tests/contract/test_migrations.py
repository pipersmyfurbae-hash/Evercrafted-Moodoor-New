"""Migrations must match the models, and must reverse cleanly.

Alembic's history is the reason SQLAlchemy + Alembic was chosen over
something lighter -- it matters once real customer data exists. A migration
that only runs forwards is not a migration, it is a one-way door.
"""

from __future__ import annotations

import pytest
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext

from backend.db.base import Base
from backend.db import models  # noqa: F401  -- populates Base.metadata


def test_models_match_the_migrated_schema(engine, created_schema) -> None:
    """Autogenerate must find nothing to do.

    A non-empty diff means someone changed a model without writing the
    migration -- which stays invisible until a deploy against a database
    that was never reset.
    """
    with engine.connect() as connection:
        context = MigrationContext.configure(connection)
        diff = compare_metadata(context, Base.metadata)

    assert not diff, "models and migrated schema disagree:\n  " + "\n  ".join(
        repr(entry) for entry in diff
    )


def test_enum_types_are_dropped_on_downgrade(engine, created_schema) -> None:
    """Guards the specific failure this migration already hit once.

    Autogenerate creates Postgres enum types implicitly via create_table but
    never emits a matching DROP TYPE, so `downgrade base` leaves them behind
    and the next `upgrade head` dies on "type already exists". The initial
    migration drops them by hand; this asserts the drops keep matching the
    enums the models actually declare.
    """
    from sqlalchemy import Enum as SAEnum

    from backend.db.migrations.versions import (  # noqa: F401
        b22d359bbdfa_initial_schema_creators_briefs_ as initial,
    )

    declared = {
        column.type.name
        for table in Base.metadata.tables.values()
        for column in table.columns
        if isinstance(column.type, SAEnum) and column.type.name
    }
    source = initial.__file__
    with open(source) as handle:
        body = handle.read()

    missing = sorted(name for name in declared if f"'{name}'" not in body)
    assert not missing, (
        f"enum type(s) {missing} are declared by the models but never dropped "
        f"in {source}. Add them to the downgrade's DROP TYPE loop or the "
        "migration becomes one-way."
    )


@pytest.mark.parametrize(
    "table_name", ["creators", "briefs", "blueprints", "orders", "royalty_ledger"]
)
def test_table_is_present_after_migration(engine, created_schema, table_name) -> None:
    from sqlalchemy import inspect

    assert table_name in inspect(engine).get_table_names()
