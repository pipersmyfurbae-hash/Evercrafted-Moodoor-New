"""Core domain tables.

Multi-creator from day one (CLAUDE.md, "Decisions Already Made"): `creators`
and `royalty_ledger` exist and every blueprint carries a `creator_id`, even
though there is one creator at launch. Retrofitting a creator_id onto a table
that already holds sold blueprints is the expensive version of this.

The floral canon deliberately has no table here. Loading the 546 SKUs into
Postgres is Sprint 3; Sprint 0 stops at the domain schema.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Index,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.config import MAX_BLUEPRINT_SCORE, MIN_MARKETPLACE_SCORE
from backend.db.base import Base, TimestampMixin, _uuid
from backend.schemas.enums import (
    BlueprintStatus,
    BlueprintType,
    CompositionFormula,
    OrderStatus,
)


def _pk() -> Mapped[str]:
    return mapped_column(String(36), primary_key=True, default=_uuid)


class Creator(Base, TimestampMixin):
    """A designer who authors sellable blueprints.

    `stripe_connect_account_id` holds a Stripe Connect **Standard** account
    id. Standard is the locked choice for launch; Express/Custom is only
    revisited if creator onboarding needs to feel fully white-labeled.
    """

    __tablename__ = "creators"

    id: Mapped[str] = _pk()
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    stripe_connect_account_id: Mapped[str | None] = mapped_column(String(64))
    royalty_rate: Mapped[Decimal] = mapped_column(
        Numeric(5, 4), nullable=False, default=Decimal("0.7000")
    )
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)

    blueprints: Mapped[list["Blueprint"]] = relationship(back_populates="creator")
    ledger_entries: Mapped[list["RoyaltyLedgerEntry"]] = relationship(
        back_populates="creator"
    )

    __table_args__ = (
        CheckConstraint(
            "royalty_rate >= 0 AND royalty_rate <= 1",
            name="royalty_rate_is_a_fraction",
        ),
    )


class Brief(Base, TimestampMixin):
    """A customer's emotional input, normalized.

    `fingerprint` is a stable hash of the normalized brief. Together with a
    blueprint's `seed` it is the pair Rule 6 promises is reproducible, so it
    is indexed: "has this exact brief been run before" is a real query.
    """

    __tablename__ = "briefs"

    id: Mapped[str] = _pk()
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    raw_input: Mapped[str] = mapped_column(Text, nullable=False)
    customer_email: Mapped[str | None] = mapped_column(String(255))
    wreath_size_inches: Mapped[int] = mapped_column(Integer, nullable=False, default=24)
    normalized: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    emotion_profile: Mapped[dict | None] = mapped_column(JSON)

    blueprints: Mapped[list["Blueprint"]] = relationship(back_populates="brief")

    __table_args__ = (
        CheckConstraint(
            "wreath_size_inches BETWEEN 12 AND 36", name="wreath_size_in_range"
        ),
    )


class Blueprint(Base, TimestampMixin):
    """A generated blueprint.

    `payload` holds the full versioned WreathBlueprint JSON; the promoted
    columns beside it exist only because they are queried or constrained.
    `schema_version` is stored so a future format change can be detected
    rather than guessed at.
    """

    __tablename__ = "blueprints"

    id: Mapped[str] = _pk()
    creator_id: Mapped[str] = mapped_column(
        ForeignKey("creators.id", ondelete="RESTRICT"), nullable=False
    )
    brief_id: Mapped[str | None] = mapped_column(
        ForeignKey("briefs.id", ondelete="SET NULL")
    )

    schema_version: Mapped[str] = mapped_column(String(16), nullable=False)
    blueprint_type: Mapped[BlueprintType] = mapped_column(
        SAEnum(BlueprintType, name="blueprint_type"),
        nullable=False,
        default=BlueprintType.SHELL,
    )
    status: Mapped[BlueprintStatus] = mapped_column(
        SAEnum(BlueprintStatus, name="blueprint_status"),
        nullable=False,
        default=BlueprintStatus.DRAFT,
    )
    formula: Mapped[CompositionFormula] = mapped_column(
        SAEnum(CompositionFormula, name="composition_formula"), nullable=False
    )

    seed: Mapped[int] = mapped_column(Integer, nullable=False)
    genome: Mapped[str | None] = mapped_column(String(255))
    score: Mapped[int | None] = mapped_column(Integer)
    preview_url: Mapped[str | None] = mapped_column(String(1024))
    pdf_url: Mapped[str | None] = mapped_column(String(1024))
    payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    creator: Mapped[Creator] = relationship(back_populates="blueprints")
    brief: Mapped[Brief | None] = relationship(back_populates="blueprints")
    orders: Mapped[list["Order"]] = relationship(back_populates="blueprint")

    __table_args__ = (
        CheckConstraint(
            f"score IS NULL OR (score >= 0 AND score <= {MAX_BLUEPRINT_SCORE})",
            name="score_within_scale",
        ),
        Index("ix_blueprints_creator_status", "creator_id", "status"),
        Index("ix_blueprints_seed", "seed"),
    )


class Order(Base, TimestampMixin):
    """A purchase.

    CLAUDE.md Rule 8: any order whose emotion profile matches
    grief/memorial/sympathy/loss must stop at `pending_review` and never
    auto-deliver. `requires_human_review` and `delivered_at` are both here
    from the first migration, and a database CHECK enforces the rule at the
    storage layer -- application code can be bypassed, a constraint cannot.
    """

    __tablename__ = "orders"

    id: Mapped[str] = _pk()
    blueprint_id: Mapped[str] = mapped_column(
        ForeignKey("blueprints.id", ondelete="RESTRICT"), nullable=False
    )
    customer_email: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[OrderStatus] = mapped_column(
        SAEnum(OrderStatus, name="order_status"),
        nullable=False,
        default=OrderStatus.GENERATED,
    )
    requires_human_review: Mapped[bool] = mapped_column(nullable=False, default=False)
    review_reason: Mapped[str | None] = mapped_column(String(255))
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    amount_cents: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    stripe_payment_intent_id: Mapped[str | None] = mapped_column(String(64))

    blueprint: Mapped[Blueprint] = relationship(back_populates="orders")
    ledger_entries: Mapped[list["RoyaltyLedgerEntry"]] = relationship(
        back_populates="order"
    )

    __table_args__ = (
        # Rule 8, enforced in the schema: an order flagged for human review
        # cannot be marked delivered, and cannot carry a delivery timestamp,
        # until it has passed through approval.
        CheckConstraint(
            "NOT (requires_human_review AND status = 'DELIVERED' AND reviewed_at IS NULL)",
            name="reviewed_before_delivery",
        ),
        CheckConstraint(
            "(status = 'DELIVERED') = (delivered_at IS NOT NULL)",
            name="delivered_at_matches_status",
        ),
        CheckConstraint("amount_cents >= 0", name="amount_not_negative"),
        Index("ix_orders_status_review", "status", "requires_human_review"),
    )


class RoyaltyLedgerEntry(Base, TimestampMixin):
    """Append-only record of what a creator is owed and paid.

    Append-only by convention: corrections are new offsetting rows, never
    edits. Money that can be silently rewritten is money nobody can audit.
    """

    __tablename__ = "royalty_ledger"

    id: Mapped[str] = _pk()
    creator_id: Mapped[str] = mapped_column(
        ForeignKey("creators.id", ondelete="RESTRICT"), nullable=False
    )
    order_id: Mapped[str | None] = mapped_column(
        ForeignKey("orders.id", ondelete="RESTRICT")
    )
    entry_type: Mapped[str] = mapped_column(String(32), nullable=False)
    amount_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    stripe_transfer_id: Mapped[str | None] = mapped_column(String(64))
    note: Mapped[str | None] = mapped_column(String(500))

    creator: Mapped[Creator] = relationship(back_populates="ledger_entries")
    order: Mapped[Order | None] = relationship(back_populates="ledger_entries")

    __table_args__ = (
        CheckConstraint(
            "entry_type IN ('sale', 'refund', 'payout', 'adjustment')",
            name="entry_type_known",
        ),
        Index("ix_royalty_ledger_creator", "creator_id", "created_at"),
    )


# Referenced by the marketplace packaging gate (Rule 7). Kept next to the
# schema so the threshold and the column it constrains stay visibly paired.
MARKETPLACE_SCORE_GATE = MIN_MARKETPLACE_SCORE
