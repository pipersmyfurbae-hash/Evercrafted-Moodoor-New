"""TRIPWIRE (b): every SKU resolves against the floral canon.

CLAUDE.md Rule 2 -- no floral SKU may be invented. Every species/SKU in any
output must resolve to a real entry in floral-canon.json. If nothing in the
canon fits, that is a flag, not a licence to substitute.
"""

from __future__ import annotations

import hashlib

import pytest

from backend.config import (
    BANNED_FLORAL_SLUGS,
    UPSTREAM_CANON_PATH,
    VENDORED_CANON_PATH,
)
from backend.modules.floral_selection.canon import CanonError, load_canon, slugify
from backend.tests.fixtures.golden_briefs import FAKE_SKU, REAL_SKUS, golden_blueprint

EXPECTED_TOTAL_SKUS = 546


@pytest.fixture(scope="module")
def canon():
    return load_canon()


def test_canon_loads_and_is_the_expected_size(canon) -> None:
    """546 SKUs: 522 profiled across 43 species plus a 24-item tail.

    Pinned deliberately. The canon is manually maintained, so a change in
    its size is a real event that should be noticed and acknowledged, not
    absorbed silently by a test that only checks "more than zero".
    """
    assert len(canon) == EXPECTED_TOTAL_SKUS, (
        f"canon holds {len(canon)} SKUs, expected {EXPECTED_TOTAL_SKUS}. "
        "If stock genuinely changed, update EXPECTED_TOTAL_SKUS and say so "
        "in the commit -- do not loosen this assertion."
    )
    assert canon.total_skus_declared == EXPECTED_TOTAL_SKUS, (
        "the canon's own total_skus_in_inventory disagrees with its contents"
    )


def test_vendored_snapshot_matches_upstream() -> None:
    """The repo copy must not drift from the skill's copy.

    Skipped rather than failed when upstream is absent: CI has no skills
    directory, and a test that cannot see upstream has nothing to say about
    whether they agree.
    """
    if not UPSTREAM_CANON_PATH.is_file():
        pytest.skip(f"upstream canon not mounted at {UPSTREAM_CANON_PATH}")

    vendored = hashlib.sha256(VENDORED_CANON_PATH.read_bytes()).hexdigest()
    upstream = hashlib.sha256(UPSTREAM_CANON_PATH.read_bytes()).hexdigest()
    assert vendored == upstream, (
        "backend/data/floral-canon.json has drifted from "
        f"{UPSTREAM_CANON_PATH}.\n  vendored: {vendored}\n  upstream: {upstream}\n"
        "Re-vendor the snapshot; upstream is authoritative."
    )


@pytest.mark.parametrize("sku", REAL_SKUS)
def test_fixture_skus_are_real(canon, sku: str) -> None:
    entry = canon.get(sku)
    assert entry.sku == sku
    assert entry.product_name, f"{sku} resolves but carries no product name"


def test_unknown_sku_raises_rather_than_substituting(canon) -> None:
    """Rule 2's real teeth: the failure mode must be loud.

    A resolver that returns a near-match on a miss is how invented florals
    reach a customer's shopping list.
    """
    with pytest.raises(CanonError) as exc:
        canon.get(FAKE_SKU)
    assert FAKE_SKU in str(exc.value)
    assert not canon.has_sku(FAKE_SKU)


def test_every_sku_in_a_generated_blueprint_resolves(canon) -> None:
    """The tripwire proper: point it at a blueprint, get a verdict."""
    blueprint = golden_blueprint()
    unresolved = canon.unresolved(blueprint.skus)
    assert not unresolved, (
        f"blueprint {blueprint.blueprint_id} references SKUs that do not "
        f"exist in the canon: {unresolved} (CLAUDE.md Rule 2)"
    )


def test_no_banned_floral_in_a_generated_blueprint(canon) -> None:
    """Policy check, separate from existence.

    A banned stem can be a real stem. Only sunflowers remain banned; the
    cherry blossom / pussy willow / twig-blossom exclusion was lifted and
    both are live in the canon.
    """
    blueprint = golden_blueprint()
    banned = canon.banned_present(blueprint.skus)
    assert not banned, f"blueprint uses banned florals: {banned}"


def test_banned_slugs_are_actually_absent_from_stock() -> None:
    """Sunflowers are banned and currently carry zero SKUs.

    If this ever fails, the canon gained a species policy forbids -- which
    is a decision to make deliberately, not a test to relax.
    """
    canon = load_canon()
    present = sorted(BANNED_FLORAL_SLUGS & canon.species_slugs())
    assert not present, (
        f"canon now stocks banned species: {present}. Either the ban is "
        "stale or the canon addition was a mistake -- resolve it explicitly."
    )


def test_lifted_exclusion_species_are_selectable(canon) -> None:
    """The lift, asserted as behaviour rather than left as a comment.

    Cherry blossom and pussy willow are live in the canon and must remain
    resolvable. If a future change re-bans them, this fails and forces the
    conversation instead of silently shrinking the palette.
    """
    for species in ("cherry-blossom", "pussy-willow"):
        assert species in canon.species_slugs(), f"{species} missing from canon"
        assert species not in BANNED_FLORAL_SLUGS, (
            f"{species} is banned in config but live in the canon -- these "
            "two disagree. See the exclusion_note in floral-canon.json."
        )


def test_slugify_matches_wgs_convention() -> None:
    assert slugify("Garden Rose") == "garden-rose"
    assert slugify("Magnolia (leaf/bud)") == "magnolia-leaf-bud"
    assert slugify("  Lamb's Ear  ") == "lamb-s-ear"
