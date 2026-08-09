"""The blueprint contract enforces the rules it can enforce structurally.

Rules 3 and 4 are shape constraints, so they belong in the schema: a
blueprint with four focal clusters should be impossible to construct, not
merely wrong once someone scores it.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend.config import BLUEPRINT_SCHEMA_VERSION
from backend.schemas.blueprint import (
    Cluster,
    Element,
    Position,
    ScoreReport,
    WreathBlueprint,
)
from backend.schemas.enums import (
    VALID_FOCAL_CLUSTER_COUNTS,
    CompositionFormula,
    ElementCategory,
    OrderStatus,
    Radius,
)
from backend.tests.fixtures.golden_briefs import SKU_GARDEN_ROSE, golden_blueprint


def _focal_cluster(index: int, angle: float) -> Cluster:
    return Cluster(
        cluster_id=f"C{index}",
        position=Position(angle_deg=angle, radius=Radius.MID),
        elements=[
            Element(
                sku=SKU_GARDEN_ROSE,
                name="Rose Bud Pick 21.5in",
                category=ElementCategory.FOCAL,
                quantity=3,
            )
        ],
    )


def _blueprint_with(cluster_count: int) -> WreathBlueprint:
    step = 360.0 / max(cluster_count, 1)
    return WreathBlueprint(
        blueprint_id="BP-TEST",
        creator_id="CR-TEST",
        seed=1,
        brief_fingerprint="fp",
        wreath_size_inches=24,
        formula=CompositionFormula.CRESCENT,
        clusters=[_focal_cluster(i + 1, i * step) for i in range(cluster_count)],
    )


@pytest.mark.parametrize("count", sorted(VALID_FOCAL_CLUSTER_COUNTS))
def test_odd_focal_cluster_counts_are_accepted(count: int) -> None:
    assert len(_blueprint_with(count).clusters) == count


@pytest.mark.parametrize("count", [2, 4, 6, 8])
def test_even_focal_cluster_counts_are_rejected(count: int) -> None:
    """CLAUDE.md Rule 4."""
    with pytest.raises(ValidationError, match="Rule 4"):
        _blueprint_with(count)


def test_formula_must_be_one_of_the_twelve() -> None:
    """CLAUDE.md Rule 3."""
    with pytest.raises(ValidationError):
        WreathBlueprint(
            blueprint_id="BP-TEST",
            creator_id="CR-TEST",
            seed=1,
            brief_fingerprint="fp",
            wreath_size_inches=24,
            formula="moon_gate_cascade",  # invented
        )


def test_there_are_exactly_twelve_formulas() -> None:
    assert len(CompositionFormula) == 12


def test_schema_version_is_pinned() -> None:
    assert golden_blueprint().schema_version == BLUEPRINT_SCHEMA_VERSION
    with pytest.raises(ValidationError):
        WreathBlueprint(
            schema_version="EC_WR_V1",
            blueprint_id="BP-TEST",
            creator_id="CR-TEST",
            seed=1,
            brief_fingerprint="fp",
            wreath_size_inches=24,
            formula=CompositionFormula.CRESCENT,
        )


def test_creator_id_is_required() -> None:
    """Multi-creator from day one -- every blueprint carries a creator."""
    with pytest.raises(ValidationError):
        WreathBlueprint(
            blueprint_id="BP-TEST",
            seed=1,
            brief_fingerprint="fp",
            wreath_size_inches=24,
            formula=CompositionFormula.CRESCENT,
        )


def test_unknown_fields_are_rejected() -> None:
    with pytest.raises(ValidationError):
        WreathBlueprint(
            blueprint_id="BP-TEST",
            creator_id="CR-TEST",
            seed=1,
            brief_fingerprint="fp",
            wreath_size_inches=24,
            formula=CompositionFormula.CRESCENT,
            midjourney_prompt="not a blueprint field",
        )


def test_duplicate_cluster_ids_are_rejected() -> None:
    """Three clusters, so the Rule 4 count check passes and this one fires."""
    duplicate = _focal_cluster(1, 200.0)
    with pytest.raises(ValidationError, match="duplicate cluster_id"):
        WreathBlueprint(
            blueprint_id="BP-TEST",
            creator_id="CR-TEST",
            seed=1,
            brief_fingerprint="fp",
            wreath_size_inches=24,
            formula=CompositionFormula.CRESCENT,
            clusters=[_focal_cluster(1, 10.0), duplicate, _focal_cluster(3, 300.0)],
        )


def test_seed_must_fit_uint32() -> None:
    with pytest.raises(ValidationError):
        WreathBlueprint(
            blueprint_id="BP-TEST",
            creator_id="CR-TEST",
            seed=2**32,
            brief_fingerprint="fp",
            wreath_size_inches=24,
            formula=CompositionFormula.CRESCENT,
        )


def test_quadrant_mass_is_derived_from_positions() -> None:
    blueprint = golden_blueprint()
    mass = blueprint.quadrant_mass()
    assert sum(mass.values()) == blueprint.total_stems
    # All three golden clusters sit between 180 and 360 degrees.
    assert mass["Q1"] == 0 and mass["Q2"] == 0
    assert mass["Q3"] > 0 and mass["Q4"] > 0


def test_skus_are_deduplicated_and_sorted() -> None:
    skus = golden_blueprint().skus
    assert skus == sorted(set(skus))


def test_dimension_scores_must_be_within_zero_to_twenty() -> None:
    with pytest.raises(ValidationError):
        ScoreReport(overall_score=100, dimension_scores={"D1_cluster_structure": 21})


def test_order_status_includes_pending_review() -> None:
    """Rule 8 needs this state to exist from the first migration."""
    assert OrderStatus.PENDING_REVIEW.value == "pending_review"
    assert [s.value for s in OrderStatus] == [
        "generated",
        "pending_review",
        "approved",
        "delivered",
    ]
