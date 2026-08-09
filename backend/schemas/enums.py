"""Closed vocabularies shared across the pipeline.

These exist as enums rather than free strings because several of them are
non-negotiable rules in CLAUDE.md. An enum makes a violation a validation
error at the module boundary instead of a design flaw discovered in a PDF.
"""

from __future__ import annotations

from enum import Enum


class CompositionFormula(str, Enum):
    """The 12 canonical composition formulas (CLAUDE.md Rule 3).

    Never extend this. A design that does not fit one of these is a flag,
    not a reason to add a thirteenth member.
    """

    CRESCENT = "crescent"
    SIDE_SWEEP = "side_sweep"
    BOTTOM_HEAVY = "bottom_heavy"
    DIAGONAL_FLOW = "diagonal_flow"
    TWIN_CLUSTER = "twin_cluster"
    CORNER_CLUSTER = "corner_cluster"
    WILD_ASYMMETRY = "wild_asymmetry"
    HALF_RING = "half_ring"
    TOP_CLUSTER = "top_cluster"
    SPIRAL_FLOW = "spiral_flow"
    CLASSIC_BALANCED = "classic_balanced"
    GARDEN_SCATTER = "garden_scatter"


class ElementCategory(str, Enum):
    """Construction layers, in build order.

    Order matters: the scoring engine's D3 dimension awards points for the
    layer sequence being exactly greenery -> secondary -> focal -> filler ->
    accent, so `LAYER_ORDER` below is derived from this rather than retyped.
    """

    GREENERY = "greenery"
    SECONDARY = "secondary"
    FOCAL = "focal"
    FILLER = "filler"
    ACCENT = "accent"


LAYER_ORDER: tuple[ElementCategory, ...] = (
    ElementCategory.GREENERY,
    ElementCategory.SECONDARY,
    ElementCategory.FOCAL,
    ElementCategory.FILLER,
    ElementCategory.ACCENT,
)


class Radius(str, Enum):
    """Radial band a cluster occupies. Placement emits these, never raw mm."""

    INNER = "inner"
    MID = "mid"
    OUTER = "outer"


class BlueprintType(str, Enum):
    """Shell is the launch default (CLAUDE.md, "Decisions Already Made").

    SHELL  -- geometry locked, florals swappable by the buyer.
    LOCKED -- exact SKUs specified; needs stock-sync or explicit
              substitution language in the listing copy.
    """

    SHELL = "shell"
    LOCKED = "locked"


class OrderStatus(str, Enum):
    """Order state machine (roadmap Phase 10 / Sprint 6b).

    PENDING_REVIEW is present from the first migration specifically so that
    Rule 8 (grief/memorial never auto-delivers) does not require a schema
    change to enforce later.
    """

    GENERATED = "generated"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    DELIVERED = "delivered"


class BlueprintStatus(str, Enum):
    """Generation lifecycle of a blueprint, distinct from its order."""

    DRAFT = "draft"
    SCORED = "scored"
    REPAIRED = "repaired"
    COMPLETE = "complete"
    FAILED = "failed"


class Season(str, Enum):
    """From wreath-genome-system/references/genome-spec.md."""

    SPRING = "spring"
    SUMMER = "summer"
    FALL = "fall"
    WINTER = "winter"
    EVERGREEN = "evergreen"
    HOLIDAY = "holiday"


class Symmetry(str, Enum):
    """From genome-spec.md."""

    ASYMMETRIC = "asymmetric"
    BILATERAL = "bilateral"
    RADIAL = "radial"


# CLAUDE.md Rule 4: focal cluster counts are odd only.
VALID_FOCAL_CLUSTER_COUNTS: frozenset[int] = frozenset({3, 5, 7})
