"""Floral canon loader and SKU resolver.

CLAUDE.md Rule 2: every species/SKU in any output must resolve to a real
entry in floral-canon.json. This module is the only place that reads the
canon, so "does this SKU exist" has exactly one answer everywhere.

Contains no AI calls and no I/O beyond reading the canon file.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from backend.config import (
    BANNED_FLORAL_SLUGS,
    UPSTREAM_CANON_PATH,
    VENDORED_CANON_PATH,
)


class CanonError(RuntimeError):
    """Raised when the canon cannot be loaded or a SKU cannot be resolved."""


@dataclass(frozen=True, slots=True)
class CanonEntry:
    """One real, purchasable stem."""

    sku: str
    product_name: str
    species: str
    species_slug: str
    color_name: str | None
    price: float | None
    primary_role: str | None

    @property
    def is_banned(self) -> bool:
        """True if policy forbids this stem regardless of canon membership.

        Kept as a property on the entry rather than a filter at load time:
        the canon is the inventory record, and a banned stem is still a real
        stem. Selection excludes them; auditing still needs to see them.
        """
        return self.species_slug in BANNED_FLORAL_SLUGS


def slugify(value: str) -> str:
    """Lowercase, hyphen-separated, matching the WGS sku-slug convention."""
    return re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")


@dataclass(frozen=True, slots=True)
class FloralCanon:
    """An immutable, indexed view over the canon file."""

    version: str
    total_skus_declared: int
    entries: tuple[CanonEntry, ...]
    _by_sku: dict[str, CanonEntry]
    _by_species_slug: dict[str, tuple[CanonEntry, ...]]
    source_path: Path
    checksum: str

    def __len__(self) -> int:
        """Unique SKUs -- the real size of the buyable inventory.

        Not the row count. The canon file carries 546 rows but only 471
        distinct SKUs: 75 are exact duplicates, same SKU and same product
        name repeated inside a single species block. Counting rows would
        overstate stock by 16% and would quietly make any per-SKU cost
        rollup wrong.
        """
        return len(self._by_sku)

    @property
    def row_count(self) -> int:
        """Rows as they appear in the file, duplicates included.

        Kept separate so a change in duplication is visible rather than
        cancelling out against a change in real inventory.
        """
        return len(self.entries)

    @property
    def duplicate_skus(self) -> dict[str, int]:
        """SKU -> number of rows, for SKUs appearing more than once."""
        counts: dict[str, int] = {}
        for entry in self.entries:
            counts[entry.sku] = counts.get(entry.sku, 0) + 1
        return {sku: n for sku, n in counts.items() if n > 1}

    def annotation_conflicts(self, field: str) -> dict[str, list]:
        """SKU -> the differing values of `field` across its duplicate rows.

        Input for Sprint 3: these are the annotations someone has to decide
        between before the selection algorithm can trust them. Identity
        fields (product_name, price) never conflict; the classification
        fields do.
        """
        rows: dict[str, list[CanonEntry]] = {}
        for entry in self.entries:
            rows.setdefault(entry.sku, []).append(entry)

        conflicts: dict[str, list] = {}
        for sku, group in rows.items():
            values = {getattr(e, field) for e in group}
            if len(values) > 1:
                conflicts[sku] = sorted(values, key=lambda v: (v is None, str(v)))
        return conflicts

    def has_sku(self, sku: str) -> bool:
        return sku.strip().upper() in self._by_sku

    def get(self, sku: str) -> CanonEntry:
        """Resolve a SKU or raise. Never returns a substitute (Rule 2)."""
        entry = self._by_sku.get(sku.strip().upper())
        if entry is None:
            raise CanonError(
                f"SKU {sku!r} does not resolve against the floral canon "
                f"({self.version}, {len(self.entries)} SKUs). CLAUDE.md Rule 2 "
                f"forbids inventing or silently substituting a floral."
            )
        return entry

    def species_slugs(self) -> frozenset[str]:
        return frozenset(self._by_species_slug)

    def unresolved(self, skus: list[str]) -> list[str]:
        """Return the subset of `skus` that do not exist. Empty means clean."""
        return sorted(s for s in skus if not self.has_sku(s))

    def banned_present(self, skus: list[str]) -> list[str]:
        """Return any SKUs whose species is under an active policy ban."""
        found = []
        for sku in skus:
            entry = self._by_sku.get(sku.strip().upper())
            if entry is not None and entry.is_banned:
                found.append(sku)
        return sorted(found)


def _parse(raw: dict, source: Path, checksum: str) -> FloralCanon:
    entries: list[CanonEntry] = []

    for species_block in raw.get("species", []):
        species = species_block.get("species", "")
        species_slug = slugify(species)
        for sku_row in species_block.get("skus", []):
            sku = str(sku_row.get("sku", "")).strip().upper()
            if not sku:
                continue
            entries.append(
                CanonEntry(
                    sku=sku,
                    product_name=sku_row.get("product_name", ""),
                    species=species,
                    species_slug=species_slug,
                    color_name=sku_row.get("color_name"),
                    price=sku_row.get("price"),
                    primary_role=sku_row.get("primary_role"),
                )
            )

    # The light-reference tail carries no species block of its own; its rows
    # are self-describing and still represent real, orderable stock.
    #
    # Species comes from the product name, NOT from the row's `category`.
    # `category` holds a role -- its values are accent/filler/focal/foliage/
    # hero/secondary -- so using it as a species would put "filler" and
    # "foliage" into the species namespace alongside Peony and Garden Rose,
    # and any code asking "do we stock this species" would get nonsense.
    for sku_row in raw.get("light_reference_tail", []):
        sku = str(sku_row.get("sku", "")).strip().upper()
        if not sku:
            continue
        product_name = sku_row.get("product_name", "")
        entries.append(
            CanonEntry(
                sku=sku,
                product_name=product_name,
                species=product_name,
                species_slug=slugify(product_name),
                color_name=sku_row.get("color_name"),
                price=sku_row.get("price"),
                # `primary_role` is the role field proper; `category` is a
                # near-duplicate that disagrees with it on some rows.
                primary_role=sku_row.get("primary_role"),
            )
        )

    # First occurrence wins, stated explicitly rather than left to dict
    # comprehension semantics (which quietly keep the LAST).
    #
    # This matters more than it looks. 75 SKUs appear twice. They always
    # agree on product name and price -- same physical stem -- but 43
    # disagree on colour label ("Magenta Pink" vs "Vibrant Fuchsia") and 28
    # on role (a peony tagged both `filler` and `focal`). Sprint 3's
    # selection algorithm keys on exactly those two fields, so "whichever
    # row happened to load last" would make selection depend on file
    # ordering -- a Rule 6 determinism hazard hiding in a data quirk.
    #
    # First-wins is deterministic but arbitrary: it is not a judgment that
    # the first annotation is the correct one. Resolving which is correct is
    # Sprint 3's job, with the conflicts surfaced by `annotation_conflicts`.
    by_sku: dict[str, CanonEntry] = {}
    for entry in entries:
        by_sku.setdefault(entry.sku, entry)
    by_species: dict[str, list[CanonEntry]] = {}
    for entry in entries:
        by_species.setdefault(entry.species_slug, []).append(entry)

    return FloralCanon(
        version=raw.get("canon_version", "unknown"),
        total_skus_declared=int(raw.get("total_skus_in_inventory", 0)),
        entries=tuple(entries),
        _by_sku=by_sku,
        _by_species_slug={k: tuple(v) for k, v in by_species.items()},
        source_path=source,
        checksum=checksum,
    )


def _read(path: Path) -> tuple[dict, str]:
    try:
        blob = path.read_bytes()
    except OSError as exc:
        raise CanonError(f"cannot read floral canon at {path}: {exc}") from exc
    checksum = hashlib.sha256(blob).hexdigest()
    try:
        return json.loads(blob), checksum
    except json.JSONDecodeError as exc:
        raise CanonError(f"floral canon at {path} is not valid JSON: {exc}") from exc


@lru_cache(maxsize=2)
def load_canon(path: Path | None = None) -> FloralCanon:
    """Load the canon, preferring the vendored snapshot.

    Resolution order:
      1. an explicit `path` argument
      2. the vendored repo snapshot -- present in CI, no skills dir needed
      3. the upstream skills copy

    The vendored snapshot is chosen over upstream on purpose: the tripwire
    must produce the same verdict in CI and on a developer machine. Drift
    between the two is caught by its own test rather than by whichever copy
    happened to load.
    """
    for candidate in (path, VENDORED_CANON_PATH, UPSTREAM_CANON_PATH):
        if candidate is not None and candidate.is_file():
            raw, checksum = _read(candidate)
            return _parse(raw, candidate, checksum)

    raise CanonError(
        "floral canon not found. Looked for an explicit path, the vendored "
        f"snapshot at {VENDORED_CANON_PATH}, and upstream at "
        f"{UPSTREAM_CANON_PATH}. Set EVERCRAFTED_CANON_PATH to override."
    )
