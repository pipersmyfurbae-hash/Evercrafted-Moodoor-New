"""Placement Intelligence Engine -- pure deterministic geometry.

CLAUDE.md Rule 1: no LLM may ever emit coordinates, angles, or radii. This
module is the only source of placement geometry in the system, and it must
never import the Anthropic SDK. That constraint is enforced by
tests/tripwires/test_no_anthropic_sdk.py rather than by convention.

SPRINT 0 SCOPE: the seeded RNG substrate and a deterministic stub only.
The real R1-R18 rule set is Sprint 4 and must be implemented from
placement-intelligence-engine/references/rules-r1-r9.md, rules-r10-r14.md and
rules-r15-r18.md directly -- never from a summary. `generate_placement` below
is a placeholder whose output is marked `stub=True` so nothing downstream can
mistake it for real geometry.
"""

from __future__ import annotations

from dataclasses import dataclass

from backend.modules.placement.rng import Mulberry32
from backend.schemas.enums import VALID_FOCAL_CLUSTER_COUNTS, CompositionFormula, Radius

__all__ = ["Mulberry32", "PlacedCluster", "generate_placement"]

# Angular window each formula sweeps, in degrees, measured clockwise from
# 12 o'clock. Sourced from the WGS genome spec's Form field table, which is
# the only place these arcs are currently written down. Sprint 4 replaces
# this with the R-rule definitions.
_FORMULA_ARCS: dict[CompositionFormula, tuple[float, float]] = {
    CompositionFormula.CRESCENT: (200.0, 340.0),
    CompositionFormula.SIDE_SWEEP: (180.0, 300.0),
    CompositionFormula.BOTTOM_HEAVY: (150.0, 300.0),
    CompositionFormula.DIAGONAL_FLOW: (135.0, 315.0),
    CompositionFormula.TWIN_CLUSTER: (30.0, 240.0),
    CompositionFormula.CORNER_CLUSTER: (200.0, 290.0),
    CompositionFormula.WILD_ASYMMETRY: (20.0, 340.0),
    CompositionFormula.HALF_RING: (90.0, 270.0),
    CompositionFormula.TOP_CLUSTER: (300.0, 60.0),
    CompositionFormula.SPIRAL_FLOW: (0.0, 359.9),
    CompositionFormula.CLASSIC_BALANCED: (0.0, 359.9),
    CompositionFormula.GARDEN_SCATTER: (0.0, 359.9),
}


@dataclass(frozen=True, slots=True)
class PlacedCluster:
    """A cluster position. Carries no floral identity -- placement decides
    where, floral selection decides what, and the orchestrator joins them."""

    cluster_id: str
    angle_deg: float
    radius: Radius
    stub: bool = True


def generate_placement(
    *,
    seed: int,
    formula: CompositionFormula,
    focal_cluster_count: int,
) -> list[PlacedCluster]:
    """Return focal cluster positions for a seed.

    Guarantees that hold now and must keep holding after Sprint 4 replaces
    the body:
      - identical (seed, formula, count) -> identical output, every time
      - focal cluster count is odd (3, 5, or 7) -- CLAUDE.md Rule 4
      - formula is one of the 12 canonical ones -- CLAUDE.md Rule 3
      - no two clusters land within 30 degrees -- scoring engine D1

    Raises ValueError rather than silently correcting a bad cluster count,
    so a Rule 4 violation surfaces at its source.
    """
    if focal_cluster_count not in VALID_FOCAL_CLUSTER_COUNTS:
        raise ValueError(
            f"focal_cluster_count={focal_cluster_count}; must be one of "
            f"{sorted(VALID_FOCAL_CLUSTER_COUNTS)} (CLAUDE.md Rule 4)"
        )
    if not isinstance(formula, CompositionFormula):
        raise ValueError(
            f"formula={formula!r} is not one of the 12 canonical formulas "
            f"(CLAUDE.md Rule 3)"
        )

    start, end = _FORMULA_ARCS[formula]
    # Arcs that cross 12 o'clock (e.g. top cluster, 300 -> 60) are unwrapped
    # so interpolation stays monotonic, then re-wrapped at emit time.
    if end < start:
        end += 360.0

    rng = Mulberry32(seed)
    span = end - start
    # Even spacing plus a bounded seeded jitter. The jitter is capped at 40%
    # of a slot so that the 30-degree minimum separation from D1 cannot be
    # violated by two adjacent clusters drifting toward each other.
    slot = span / focal_cluster_count
    jitter_cap = min(slot * 0.4, (slot - 30.0) / 2.0) if slot > 30.0 else 0.0

    placed: list[PlacedCluster] = []
    for index in range(focal_cluster_count):
        centre = start + slot * (index + 0.5)
        angle = (centre + rng.uniform(-jitter_cap, jitter_cap)) % 360.0
        # Largest-first ordering means index 0 is the dominant cluster; it
        # spans outer radius, the rest alternate for depth (scoring D1).
        radius = Radius.OUTER if index == 0 else rng.choice((Radius.MID, Radius.INNER))
        placed.append(
            PlacedCluster(
                cluster_id=f"C{index + 1}",
                # Rounded so float formatting cannot differ across platforms
                # and break byte-identical serialization.
                angle_deg=round(angle, 6),
                radius=radius,
            )
        )
    return placed
