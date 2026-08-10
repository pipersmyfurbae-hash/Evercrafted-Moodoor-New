#!/usr/bin/env python3
"""Refresh the vendored floral canon snapshot from upstream.

The canon is manually maintained and has no live stock feed, so the repo
carries a snapshot at backend/data/floral-canon.json. That snapshot exists so
the SKU tripwire runs in CI without the skills directory mounted -- upstream
stays authoritative, and this script is how the two are reconciled.

Usage:
    python scripts/refresh_canon.py            # report differences only
    python scripts/refresh_canon.py --apply    # copy upstream over the snapshot

    # Point at a canon somewhere else:
    EVERCRAFTED_CANON_PATH=/path/to/floral-canon.json python scripts/refresh_canon.py

Run it when the canon changes upstream. `test_vendored_snapshot_matches_upstream`
fails whenever the two disagree and upstream is reachable, so drift surfaces on
the next test run rather than whenever someone happens to notice.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from backend.config import UPSTREAM_CANON_PATH, VENDORED_CANON_PATH  # noqa: E402


def _checksum(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sku_index(path: Path) -> dict[str, str]:
    """Map SKU -> product name, across both species blocks and the tail."""
    raw = json.loads(path.read_text())
    index: dict[str, str] = {}
    for block in raw.get("species", []):
        for row in block.get("skus", []):
            sku = str(row.get("sku", "")).strip().upper()
            if sku:
                index[sku] = f"{block.get('species', '?')} / {row.get('product_name', '')}"
    for row in raw.get("light_reference_tail", []):
        sku = str(row.get("sku", "")).strip().upper()
        if sku:
            index[sku] = f"tail / {row.get('product_name', '')}"
    return index


def _species(path: Path) -> set[str]:
    raw = json.loads(path.read_text())
    return {block.get("species", "") for block in raw.get("species", [])}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="write upstream over the vendored snapshot (default: report only)",
    )
    args = parser.parse_args()

    if not UPSTREAM_CANON_PATH.is_file():
        print(f"upstream canon not found: {UPSTREAM_CANON_PATH}")
        print("Set EVERCRAFTED_CANON_PATH to point at it.")
        return 2
    if not VENDORED_CANON_PATH.is_file():
        print(f"vendored snapshot missing: {VENDORED_CANON_PATH}")
        if args.apply:
            shutil.copy2(UPSTREAM_CANON_PATH, VENDORED_CANON_PATH)
            print("created it from upstream.")
            return 0
        return 2

    upstream_sum = _checksum(UPSTREAM_CANON_PATH)
    vendored_sum = _checksum(VENDORED_CANON_PATH)

    print(f"upstream: {UPSTREAM_CANON_PATH}\n  sha256 {upstream_sum}")
    print(f"vendored: {VENDORED_CANON_PATH}\n  sha256 {vendored_sum}\n")

    if upstream_sum == vendored_sum:
        print("identical — nothing to do.")
        return 0

    before, after = _sku_index(VENDORED_CANON_PATH), _sku_index(UPSTREAM_CANON_PATH)
    added = sorted(set(after) - set(before))
    removed = sorted(set(before) - set(after))
    species_added = sorted(_species(UPSTREAM_CANON_PATH) - _species(VENDORED_CANON_PATH))
    species_removed = sorted(_species(VENDORED_CANON_PATH) - _species(UPSTREAM_CANON_PATH))

    print(f"SKU count: {len(before)} -> {len(after)}")
    for label, skus in (("added", added), ("removed", removed)):
        if skus:
            print(f"\n  {len(skus)} {label}:")
            for sku in skus[:20]:
                source = after.get(sku) or before.get(sku)
                print(f"    {sku:<14} {source}")
            if len(skus) > 20:
                print(f"    ... and {len(skus) - 20} more")
    if species_added:
        print(f"\n  species added: {species_added}")
    if species_removed:
        print(f"  species removed: {species_removed}")

    # A removed SKU is the case that actually breaks things: a shipped
    # blueprint may already reference it, and Rule 2 forbids substituting
    # silently. Say so rather than letting it pass as a count change.
    if removed:
        print(
            f"\n  WARNING: {len(removed)} SKU(s) disappeared upstream. Any "
            "blueprint already referencing one will fail the SKU tripwire. "
            "Rule 2 forbids silent substitution — those designs need an "
            "explicit decision, not an auto-fix."
        )

    if not args.apply:
        print("\nreport only. Re-run with --apply to update the snapshot.")
        return 1

    shutil.copy2(UPSTREAM_CANON_PATH, VENDORED_CANON_PATH)
    print(f"\nsnapshot updated ({len(after)} SKUs).")
    if len(after) != len(before):
        print(
            "  NEXT: update EXPECTED_TOTAL_SKUS in "
            "backend/tests/tripwires/test_sku_resolution.py to "
            f"{len(after)} and note the change in the commit message."
        )
    print("  Then: pytest backend/tests/tripwires")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
