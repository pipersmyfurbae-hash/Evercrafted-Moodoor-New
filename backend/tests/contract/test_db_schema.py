"""Schema-level guarantees.

Rule 8 is business-critical, so it is enforced by a database CHECK rather
than by application code alone. Application code can be bypassed by a
migration script, an admin console, or a future endpoint that forgets;
a constraint cannot.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError

from backend.db.models import Blueprint, Creator, Order, RoyaltyLedgerEntry
from backend.schemas.enums import BlueprintType, CompositionFormula, OrderStatus

pytestmark = pytest.mark.usefixtures("created_schema")

EXPECTED_TABLES = {"creators", "briefs", "blueprints", "orders", "royalty_ledger"}


def test_expected_tables_exist(engine) -> None:
    tables = set(inspect(engine).get_table_names())
    assert EXPECTED_TABLES <= tables, f"missing: {sorted(EXPECTED_TABLES - tables)}"


def test_creators_and_royalty_ledger_exist(engine) -> None:
    """Multi-creator from day one, even with one creator at launch."""
    tables = set(inspect(engine).get_table_names())
    assert "creators" in tables
    assert "royalty_ledger" in tables


def test_every_blueprint_carries_a_creator_id(engine) -> None:
    columns = {c["name"]: c for c in inspect(engine).get_columns("blueprints")}
    assert "creator_id" in columns
    assert columns["creator_id"]["nullable"] is False


def _creator(session) -> Creator:
    creator = Creator(display_name="Evercrafted", email="creator@example.test")
    session.add(creator)
    session.flush()
    return creator


def _blueprint(session, creator: Creator) -> Blueprint:
    blueprint = Blueprint(
        creator_id=creator.id,
        schema_version="EC_WR_V2",
        blueprint_type=BlueprintType.SHELL,
        formula=CompositionFormula.CRESCENT,
        seed=20260809,
        payload={},
    )
    session.add(blueprint)
    session.flush()
    return blueprint


def test_blueprint_requires_an_existing_creator(db_session) -> None:
    db_session.add(
        Blueprint(
            creator_id="does-not-exist",
            schema_version="EC_WR_V2",
            formula=CompositionFormula.CRESCENT,
            seed=1,
            payload={},
        )
    )
    with pytest.raises(IntegrityError):
        db_session.flush()


def test_score_cannot_exceed_the_scale(db_session) -> None:
    creator = _creator(db_session)
    blueprint = _blueprint(db_session, creator)
    blueprint.score = 121
    with pytest.raises(IntegrityError):
        db_session.flush()


def test_flagged_order_cannot_be_delivered_unreviewed(db_session) -> None:
    """CLAUDE.md Rule 8, enforced in the schema.

    A grief/memorial order marked delivered without a review timestamp must
    be rejected by the database itself.
    """
    creator = _creator(db_session)
    blueprint = _blueprint(db_session, creator)
    db_session.add(
        Order(
            blueprint_id=blueprint.id,
            customer_email="buyer@example.test",
            status=OrderStatus.DELIVERED,
            requires_human_review=True,
            review_reason="grief",
            reviewed_at=None,
            delivered_at=datetime.now(timezone.utc),
        )
    )
    with pytest.raises(IntegrityError):
        db_session.flush()


def test_reviewed_flagged_order_may_be_delivered(db_session) -> None:
    """The same order passes once it has actually been reviewed."""
    creator = _creator(db_session)
    blueprint = _blueprint(db_session, creator)
    now = datetime.now(timezone.utc)
    db_session.add(
        Order(
            blueprint_id=blueprint.id,
            customer_email="buyer@example.test",
            status=OrderStatus.DELIVERED,
            requires_human_review=True,
            review_reason="grief",
            reviewed_at=now,
            delivered_at=now,
        )
    )
    db_session.flush()


def test_delivered_at_must_match_status(db_session) -> None:
    creator = _creator(db_session)
    blueprint = _blueprint(db_session, creator)
    db_session.add(
        Order(
            blueprint_id=blueprint.id,
            customer_email="buyer@example.test",
            status=OrderStatus.PENDING_REVIEW,
            delivered_at=datetime.now(timezone.utc),
        )
    )
    with pytest.raises(IntegrityError):
        db_session.flush()


def test_royalty_entry_type_is_constrained(db_session) -> None:
    creator = _creator(db_session)
    db_session.add(
        RoyaltyLedgerEntry(
            creator_id=creator.id, entry_type="vibes", amount_cents=100
        )
    )
    with pytest.raises(IntegrityError):
        db_session.flush()


@pytest.mark.parametrize("entry_type", ["sale", "refund", "payout", "adjustment"])
def test_known_royalty_entry_types_are_accepted(db_session, entry_type: str) -> None:
    creator = _creator(db_session)
    db_session.add(
        RoyaltyLedgerEntry(
            creator_id=creator.id, entry_type=entry_type, amount_cents=1500
        )
    )
    db_session.flush()
