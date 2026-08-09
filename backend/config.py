"""Backend-wide configuration constants.

Anything a non-negotiable rule depends on lives here as a single named
constant, so that flipping a policy is a one-line change rather than a
grep-and-pray across modules.
"""

from __future__ import annotations

import os
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent
REPO_ROOT = BACKEND_ROOT.parent

# --- Floral policy -------------------------------------------------------
#
# CLAUDE.md Rule 5 originally banned cherry blossom, pussy willow,
# twig/dried-wheat blossoms and sunflowers. The cherry blossom / pussy
# willow / twig-blossom portion was lifted -- floral-canon.json records the
# lift ("exclusion_note") and evercrafted-floral-selector/SKILL.md marks the
# old list superseded. Both species are live in the canon.
#
# Sunflowers remain banned. They carry zero SKUs in the canon today, so the
# rule is currently unenforceable-by-absence; it is kept explicit so that a
# future canon addition cannot quietly introduce one.
#
# Two files still encode the old ban and are known-stale:
#   - evercrafted-floral-selector/references/floral-canon.md ("permanent ban")
#   - blueprint-scoring-repair-engine/SKILL.md D6 (5 pts for "no banned florals")
# The scoring one needs reconciling in Sprint 5 or cherry-blossom designs will
# silently lose 5/120 against the >=80 packaging gate.
BANNED_FLORAL_SLUGS: frozenset[str] = frozenset({"sunflower"})

# --- Floral canon --------------------------------------------------------
#
# The canon is manually maintained and has no live stock feed (CLAUDE.md,
# "Decisions Already Made"). A snapshot is vendored into the repo so the SKU
# tripwire runs in CI without the skills directory mounted; the upstream copy
# stays authoritative and `tests/tripwires/test_sku_resolution.py` flags drift
# between the two whenever upstream is reachable.
VENDORED_CANON_PATH = BACKEND_ROOT / "data" / "floral-canon.json"
UPSTREAM_CANON_PATH = Path(
    os.environ.get(
        "EVERCRAFTED_CANON_PATH",
        "/root/.claude/skills/evercrafted-floral-canon/references/floral-canon.json",
    )
)

# --- Blueprint schema ----------------------------------------------------
#
# Bumped only when a field is added, removed, or reordered. Parsers must check
# this before decoding, mirroring the WGS genome version discipline.
BLUEPRINT_SCHEMA_VERSION = "EC_WR_V2"

# --- Quality gate --------------------------------------------------------
# CLAUDE.md Rule 7: no blueprint may be packaged for sale below 80/120.
MIN_MARKETPLACE_SCORE = 80
MAX_BLUEPRINT_SCORE = 120

# --- Human review --------------------------------------------------------
# CLAUDE.md Rule 8: these emotion tags force an order to pending_review and
# must never auto-deliver. Matching logic lands in Sprint 6b; the vocabulary
# is fixed here so the schema and the router cannot disagree about it.
#
# Deliberately the exact four from Rule 8, not a superset. The WGS emotion
# vocabulary also carries "remembrance", which reads memorial-adjacent -- but
# widening a business-critical trigger set is Bret's call, not a silent one.
# Open question for Sprint 6b.
REVIEW_REQUIRED_EMOTIONS: frozenset[str] = frozenset(
    {"grief", "memorial", "sympathy", "loss"}
)

# --- Database ------------------------------------------------------------
# Never hardcode a connection string. Railway provides this in deployment;
# local runs point it at an ephemeral cluster.
DATABASE_URL = os.environ.get("DATABASE_URL", "")
