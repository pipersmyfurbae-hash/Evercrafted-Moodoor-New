"""Backend-wide configuration constants.

Anything a non-negotiable rule depends on lives here as a single named
constant, so that flipping a policy is a one-line change rather than a
grep-and-pray across modules.
"""

from __future__ import annotations

import os
import re
from collections.abc import Iterable
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
# must never auto-deliver. Routing lands in Sprint 6b; the vocabulary lives
# here so the schema and the router cannot disagree about it.
#
# Widened past Rule 8's original four after a scan of every emotion
# vocabulary in the ecosystem: the WGS canonical slugs (genome-spec.md), the
# floral selector's emotion wheel (7 sectors, 19 terms in SAD alone), and the
# emotional-design-translator's atmosphere archetypes.
#
# The line drawn is BEREAVEMENT, not sadness. A term qualifies when it
# denotes a death or a loss, not when it merely reads sad. That distinction
# is load-bearing: the SAD sector carries lonely, despair, hurt, empty,
# abandoned, fragile and a dozen more, and routing all of them to a human
# would make the review queue mostly false positives -- at which point it
# gets rubber-stamped and protects nobody.
#
# Asymmetric costs justify erring inclusive within bereavement itself: a
# false positive costs a reviewer under a minute, a false negative
# auto-delivers an unreviewed memorial blueprint, which is the exact harm
# Rule 8 exists to prevent.
REVIEW_REQUIRED_EMOTIONS: frozenset[str] = frozenset(
    {
        # Rule 8's original four.
        "grief",
        "memorial",
        "sympathy",
        "loss",
        # WGS canonical slug. Memorial in ordinary use.
        "remembrance",
        # Bereavement vocabulary found across the ecosystem's emotion tables.
        "mourning",
        "bereavement",
        "condolence",
        "funeral",
        "sorrow",
        "elegy",
        "in-memory",
        # Judgment call, and the one to drop first if the queue runs hot:
        # a WGS slug that covers both sacred/architectural stillness
        # ("Winter Reverence" in the translator) and memorial registers.
        # Included because missing a real memorial costs more than a
        # needless review.
        "reverence",
    }
)

# Scanned and deliberately EXCLUDED -- sadness or mood, not bereavement.
# Recorded so the next person to ask "why isn't melancholy in there?" gets an
# answer instead of re-litigating it.
#   melancholy, lonely, isolated, despair, depressed, hurt, empty, abandoned,
#   fragile, vulnerable, powerless, disappointed, victimised, guilty,
#   remorseful, ashamed, embarrassed, inferior
# "legacy" and "tribute" were also excluded: both appear in the ecosystem but
# read commemorative-of-the-living at least as often as memorial.


# Word stems per trigger, matched against whole tokens by prefix.
#
# Prefix-on-token rather than plain substring, for a specific reason: "loss"
# is a substring of "glossy", and glossy is a texture word used constantly in
# this domain. Token matching keeps "glossy" from routing an order to a
# bereavement queue while still catching "grieving" and "bereaved".
_REVIEW_STEMS: dict[str, tuple[str, ...]] = {
    "grief": ("grief", "griev"),
    "memorial": ("memorial",),
    "sympathy": ("sympath",),
    "loss": ("loss", "lost"),
    "remembrance": ("remembr", "remember"),
    "mourning": ("mourn",),
    "bereavement": ("bereav",),
    "condolence": ("condol",),
    "funeral": ("funeral",),
    "sorrow": ("sorrow",),
    "elegy": ("elegy", "elegiac"),
    "reverence": ("reveren",),
}

# Phrases matched against the whole normalized string.
#
# "memory" is deliberately NOT a stem. The product's entire input is a
# customer's memory -- CLAUDE.md opens by describing it that way -- so a
# bare "memory" token would flag every order ever placed. Only the
# commemorative phrasings trigger.
_REVIEW_PHRASES: dict[str, tuple[str, ...]] = {
    "in-memory": ("in-memory", "in-loving-memory", "in-memoriam", "memoriam"),
}


# What may follow a stem for the match to count as an inflection of it.
#
# A bare prefix test is too loose: "lossless" starts with "loss" but is not a
# form of it. Requiring a real word-ending keeps "grieving", "bereaved" and
# "sorrowful" while rejecting words that merely begin the same way.
_INFLECTIONS: frozenset[str] = frozenset(
    {
        "",
        "s", "es", "ies",
        "e", "ed", "ing",
        "y", "al", "ce",
        "ance", "ances", "ence", "ences",
        "ement", "ements",
        "ful", "fully",
    }
)


def _normalize_emotion(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")


def _token_matches_stem(token: str, stem: str) -> bool:
    return token.startswith(stem) and token[len(stem) :] in _INFLECTIONS


def requires_human_review(emotions: Iterable[str]) -> str | None:
    """Return the trigger term that matched, or None.

    Matches word stems rather than exact slugs, so "grieving", "bereaved"
    and "in memory of my mother" all trigger. An exact-set check would let
    the most natural phrasings straight through, which is the failure that
    matters: customers do not write their feelings in slug form, and a real
    memorial order auto-delivering because the word arrived conjugated is
    precisely what Rule 8 exists to prevent.

    Returns the term rather than a bool so an order's `review_reason` can
    name the word that caused it.
    """
    for raw in emotions:
        normalized = _normalize_emotion(raw)
        if not normalized:
            continue

        for trigger, phrases in _REVIEW_PHRASES.items():
            if any(phrase in normalized for phrase in phrases):
                return trigger

        tokens = normalized.split("-")
        for trigger in sorted(REVIEW_REQUIRED_EMOTIONS):
            for stem in _REVIEW_STEMS.get(trigger, (trigger,)):
                if any(_token_matches_stem(token, stem) for token in tokens):
                    return trigger
    return None

# --- Database ------------------------------------------------------------
# Never hardcode a connection string. Railway provides this in deployment;
# local runs point it at an ephemeral cluster.
DATABASE_URL = os.environ.get("DATABASE_URL", "")
