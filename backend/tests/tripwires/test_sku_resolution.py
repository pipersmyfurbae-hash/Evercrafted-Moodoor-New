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

# Rows in the file: 522 profiled across 43 species plus a 24-item tail.
EXPECTED_CANON_ROWS = 546
# Distinct SKUs among those rows. The gap is 75 exact duplicates -- same SKU,
# same product name, repeated inside one species block. This is the number
# that describes actual buyable inventory.
EXPECTED_UNIQUE_SKUS = 471
EXPECTED_DUPLICATE_SKUS = 75
# Among those duplicates: identity fields always agree, classification
# fields do not. Sprint 3 input, pinned so the numbers moving is visible.
EXPECTED_COLOUR_CONFLICTS = 43
EXPECTED_ROLE_CONFLICTS = 28


@pytest.fixture(scope="module")
def canon():
    return load_canon()


def test_canon_loads_and_is_the_expected_size(canon) -> None:
    """Both counts pinned, deliberately.

    The canon is manually maintained, so a size change is a real event to be
    noticed and acknowledged. Pinning rows and unique SKUs separately means a
    genuine stock change cannot hide by cancelling out against a change in
    duplication.
    """
    assert len(canon) == EXPECTED_UNIQUE_SKUS, (
        f"canon holds {len(canon)} unique SKUs, expected "
        f"{EXPECTED_UNIQUE_SKUS}. If stock genuinely changed, update this "
        "constant and say so in the commit -- do not loosen the assertion."
    )
    assert canon.row_count == EXPECTED_CANON_ROWS, (
        f"canon has {canon.row_count} rows, expected {EXPECTED_CANON_ROWS}"
    )


def test_canon_declared_total_counts_rows_not_unique_skus(canon) -> None:
    """Documents a known discrepancy in the canon file itself.

    `total_skus_in_inventory` is 546, which is the row count. Real distinct
    inventory is 471. Anything reading the declared figure as a SKU count --
    a COGS rollup, a "how much do we stock" answer -- overstates by 16%.

    Asserted rather than merely noted so that if the canon is ever cleaned
    up, this fails and prompts the constants above to be updated together.
    """
    assert canon.total_skus_declared == EXPECTED_CANON_ROWS
    assert canon.total_skus_declared != len(canon)


def test_duplicate_rows_describe_the_same_physical_stem(canon) -> None:
    """The 75 duplicates must stay benign.

    Benign means: every row sharing a SKU describes the same physical
    product -- same name, colour and price -- so deduplicating by SKU loses
    nothing real. If two rows ever share a SKU while describing different
    stems, dedup silently drops a product, and every downstream shopping
    list is wrong. That is a data emergency, not a tidy-up.
    """
    duplicates = canon.duplicate_skus
    assert len(duplicates) == EXPECTED_DUPLICATE_SKUS, (
        f"{len(duplicates)} duplicated SKUs, expected {EXPECTED_DUPLICATE_SKUS}"
    )

    # Identity is product name and price. Both are stable across every
    # duplicate today, which is what makes dedup safe.
    assert not canon.annotation_conflicts("product_name"), (
        "SKU(s) appear more than once under DIFFERENT product names. "
        "Deduplicating by SKU would drop a real stem -- resolve the canon "
        "data before trusting any selection built on it."
    )
    assert not canon.annotation_conflicts("price"), (
        "SKU(s) appear more than once at different prices. Any shopping "
        "list or COGS figure built on this is wrong."
    )


def test_annotation_conflicts_are_pinned(canon) -> None:
    """Same stem, disagreeing classification. Pinned, not fixed.

    The duplicate rows agree on which product it is and what it costs, but
    not on how it is labelled: 43 SKUs carry two colour names ("Magenta
    Pink" vs "Vibrant Fuchsia"), and 28 carry two roles (a peony tagged both
    `filler` and `focal`).

    This is Sprint 3's problem to resolve with real judgment -- the loader
    cannot know which annotation is right. What the loader guarantees is
    that the choice is deterministic (first row wins), so the conflict
    cannot express itself as non-reproducible output under Rule 6.

    Pinned at today's counts so the numbers moving is something someone
    notices.
    """
    colour_conflicts = canon.annotation_conflicts("color_name")
    role_conflicts = canon.annotation_conflicts("primary_role")

    assert len(colour_conflicts) == EXPECTED_COLOUR_CONFLICTS, (
        f"{len(colour_conflicts)} SKUs carry conflicting colour names, "
        f"expected {EXPECTED_COLOUR_CONFLICTS}"
    )
    assert len(role_conflicts) == EXPECTED_ROLE_CONFLICTS, (
        f"{len(role_conflicts)} SKUs carry conflicting roles, expected "
        f"{EXPECTED_ROLE_CONFLICTS}"
    )


def test_dedup_is_deterministic_regardless_of_conflicts(canon) -> None:
    """The Rule 6 guarantee that makes the conflicts survivable.

    Loading the canon twice must resolve every conflicted SKU the same way.
    If it did not, two identical briefs could select differently coloured
    stems from the same inventory.
    """
    from backend.modules.floral_selection.canon import load_canon

    load_canon.cache_clear()
    first = {sku: load_canon().get(sku) for sku in canon.annotation_conflicts("color_name")}
    load_canon.cache_clear()
    second = {sku: load_canon().get(sku) for sku in first}

    differing = sorted(s for s in first if first[s] != second[s])
    assert not differing, (
        f"SKU(s) {differing} resolved differently across two loads of the "
        "same file -- dedup is not deterministic (CLAUDE.md Rule 6)."
    )


def test_species_namespace_holds_species_not_roles(canon) -> None:
    """Roles must never leak into the species namespace.

    The tail's `category` field holds accent/filler/focal/foliage/hero/
    secondary -- roles, not species. Deriving species from it would put
    "filler" beside "Peony", and any "do we stock this species" check would
    start returning nonsense.
    """
    roles = {"filler", "secondary", "focal", "greenery", "accent", "foliage", "hero"}
    leaked = sorted(roles & canon.species_slugs())
    assert not leaked, f"role names leaked into the species namespace: {leaked}"


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
