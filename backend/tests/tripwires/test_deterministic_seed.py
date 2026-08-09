"""TRIPWIRE (c): same seed, same output.

CLAUDE.md Rule 6 -- the same seed and the same inputs must always produce
the identical blueprint. This is the property the whole business rests on:
a blueprint sold twice must be the same blueprint twice.

SPRINT 0 NOTE, and the reason this file is written the way it is: the real
R1-R18 placement engine does not exist yet. `generate_placement` is a
deterministic stub. A tripwire written against a stub that returns a
constant would pass forever and guard nothing, so these tests assert
properties that must survive Sprint 4 replacing the body:

  - identical inputs produce byte-identical output
  - different seeds produce different output (proves the seed is actually
    consumed -- a hardcoded return value would pass the first test alone)
  - the RNG stream itself is reproducible and position-dependent

`test_seed_actually_changes_the_output` is the load-bearing one. It is what
stops this file from degenerating into a test of nothing.
"""

from __future__ import annotations

import json

import pytest

from backend.modules.placement import generate_placement
from backend.modules.placement.rng import Mulberry32
from backend.schemas.enums import CompositionFormula
from backend.tests.fixtures.golden_briefs import GOLDEN_SEED, golden_blueprint

SEED_A = GOLDEN_SEED
SEED_B = GOLDEN_SEED + 1


def _serialize(clusters) -> str:
    return json.dumps(
        [
            {
                "cluster_id": c.cluster_id,
                "angle_deg": c.angle_deg,
                "radius": c.radius.value,
            }
            for c in clusters
        ],
        sort_keys=True,
        separators=(",", ":"),
    )


# --- the RNG substrate ---------------------------------------------------


def test_rng_stream_is_reproducible() -> None:
    a = Mulberry32(SEED_A)
    b = Mulberry32(SEED_A)
    assert [a.next_uint32() for _ in range(64)] == [b.next_uint32() for _ in range(64)]


def test_rng_stream_differs_by_seed() -> None:
    a = [Mulberry32(SEED_A).next_uint32() for _ in range(8)]
    b = [Mulberry32(SEED_B).next_uint32() for _ in range(8)]
    assert a != b, "two different seeds produced the same stream"


def test_rng_stays_in_uint32_range() -> None:
    rng = Mulberry32(SEED_A)
    for _ in range(2048):
        value = rng.next_uint32()
        assert 0 <= value <= 0xFFFFFFFF
        assert isinstance(value, int)


def test_rng_floats_are_unit_interval() -> None:
    rng = Mulberry32(SEED_A)
    for _ in range(2048):
        value = rng.next_float()
        assert 0.0 <= value < 1.0


def test_rng_reset_replays_the_same_stream() -> None:
    rng = Mulberry32(SEED_A)
    first = [rng.next_uint32() for _ in range(16)]
    rng.reset()
    assert [rng.next_uint32() for _ in range(16)] == first


def test_rng_rejects_out_of_range_seed() -> None:
    with pytest.raises(ValueError):
        Mulberry32(-1)
    with pytest.raises(ValueError):
        Mulberry32(2**32)


# --- placement -----------------------------------------------------------


@pytest.mark.parametrize("formula", list(CompositionFormula))
@pytest.mark.parametrize("count", [3, 5, 7])
def test_same_seed_produces_byte_identical_placement(
    formula: CompositionFormula, count: int
) -> None:
    """Across every formula and every legal cluster count."""
    first = generate_placement(seed=SEED_A, formula=formula, focal_cluster_count=count)
    second = generate_placement(seed=SEED_A, formula=formula, focal_cluster_count=count)
    assert _serialize(first) == _serialize(second), (
        f"{formula.value}/{count} clusters was not reproducible from seed "
        f"{SEED_A} (CLAUDE.md Rule 6)"
    )


def test_placement_is_stable_across_repeated_runs() -> None:
    runs = {
        _serialize(
            generate_placement(
                seed=SEED_A,
                formula=CompositionFormula.CRESCENT,
                focal_cluster_count=5,
            )
        )
        for _ in range(25)
    }
    assert len(runs) == 1, f"25 runs of one seed produced {len(runs)} distinct outputs"


def test_seed_actually_changes_the_output() -> None:
    """The anti-stub guard.

    If placement ever stops consuming its seed -- a hardcoded template, a
    cached result, a refactor that drops the RNG -- every other test here
    still passes and this one fails. Do not delete it to make a sprint green.
    """
    a = _serialize(
        generate_placement(
            seed=SEED_A, formula=CompositionFormula.CRESCENT, focal_cluster_count=5
        )
    )
    b = _serialize(
        generate_placement(
            seed=SEED_B, formula=CompositionFormula.CRESCENT, focal_cluster_count=5
        )
    )
    assert a != b, (
        "two different seeds produced identical placement. The seed is not "
        "reaching the geometry -- placement is not actually seeded."
    )


@pytest.mark.parametrize("count", [3, 5, 7])
def test_placement_honours_odd_cluster_counts(count: int) -> None:
    placed = generate_placement(
        seed=SEED_A, formula=CompositionFormula.CRESCENT, focal_cluster_count=count
    )
    assert len(placed) == count
    assert len({c.cluster_id for c in placed}) == count


@pytest.mark.parametrize("count", [2, 4, 6, 0, 8])
def test_placement_rejects_even_cluster_counts(count: int) -> None:
    """CLAUDE.md Rule 4 -- and it must raise, not quietly round to odd."""
    with pytest.raises(ValueError, match="Rule 4"):
        generate_placement(
            seed=SEED_A, formula=CompositionFormula.CRESCENT, focal_cluster_count=count
        )


def test_placement_angles_are_in_range() -> None:
    for formula in CompositionFormula:
        for c in generate_placement(seed=SEED_A, formula=formula, focal_cluster_count=5):
            assert 0.0 <= c.angle_deg < 360.0, f"{formula.value}: {c.angle_deg}"


def test_placement_output_is_still_marked_a_stub() -> None:
    """Fails the moment Sprint 4 lands real geometry.

    That failure is the point: it is the prompt to re-read this file and
    confirm the determinism guarantees still hold against the real engine,
    rather than assuming they carried over.
    """
    placed = generate_placement(
        seed=SEED_A, formula=CompositionFormula.CRESCENT, focal_cluster_count=3
    )
    assert all(c.stub for c in placed), (
        "placement no longer reports itself as a stub -- the real R1-R18 "
        "engine has landed. Re-read backend/tests/tripwires/"
        "test_deterministic_seed.py, confirm every determinism guarantee "
        "still holds, then remove this test."
    )


# --- blueprint serialization ---------------------------------------------


def test_blueprint_serialization_is_byte_identical() -> None:
    assert golden_blueprint().canonical_json() == golden_blueprint().canonical_json()


def test_blueprint_serialization_differs_by_seed() -> None:
    assert (
        golden_blueprint(seed=SEED_A).canonical_json()
        != golden_blueprint(seed=SEED_B).canonical_json()
    )


def test_canonical_json_is_key_order_independent() -> None:
    """Byte comparison must test content, not dict insertion order."""
    blueprint = golden_blueprint()
    reparsed = type(blueprint).model_validate(json.loads(blueprint.canonical_json()))
    assert reparsed.canonical_json() == blueprint.canonical_json()
