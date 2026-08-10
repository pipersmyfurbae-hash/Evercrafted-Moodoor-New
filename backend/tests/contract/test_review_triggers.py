"""Rule 8's trigger vocabulary.

CLAUDE.md Rule 8 is business-critical: any order whose emotion profile
matches grief/memorial/sympathy/loss stops at pending_review and never
auto-delivers. These tests pin both halves of the judgment -- what triggers
and what deliberately does not -- so neither can drift silently.
"""

from __future__ import annotations

import pytest

from backend.config import REVIEW_REQUIRED_EMOTIONS, requires_human_review

# Rule 8's literal four. These can never leave the set.
RULE_8_ORIGINAL = ("grief", "memorial", "sympathy", "loss")


@pytest.mark.parametrize("emotion", RULE_8_ORIGINAL)
def test_rule_8_original_four_always_trigger(emotion: str) -> None:
    assert emotion in REVIEW_REQUIRED_EMOTIONS
    assert requires_human_review([emotion]) is not None


@pytest.mark.parametrize(
    "emotion",
    ["remembrance", "mourning", "bereavement", "condolence", "funeral", "reverence"],
)
def test_widened_bereavement_terms_trigger(emotion: str) -> None:
    assert requires_human_review([emotion]) is not None


@pytest.mark.parametrize(
    "phrase",
    [
        "grieving",
        "Grief",
        "  GRIEF  ",
        "bereaved",
        "in memory of my mother",
        "in-memory",
        "deep sorrow",
        "a memorial for dad",
        "sympathy arrangement",
        "remembering her",
    ],
)
def test_natural_phrasing_triggers(phrase: str) -> None:
    """Customers do not write their feelings in slug form.

    An exact-match check would let every one of these through, which is the
    failure mode that matters -- a real memorial order auto-delivering
    because the word arrived conjugated.
    """
    assert requires_human_review([phrase]) is not None, f"{phrase!r} did not trigger"


@pytest.mark.parametrize(
    "emotion",
    [
        "melancholy",
        "lonely",
        "isolated",
        "despair",
        "hurt",
        "empty",
        "abandoned",
        "fragile",
        "vulnerable",
        "disappointed",
        "joy",
        "celebration",
        "warmth",
        "nostalgia",
        "peace",
        "gratitude",
    ],
)
def test_sadness_and_mood_do_not_trigger(emotion: str) -> None:
    """The bereavement/sadness line, asserted.

    If these start triggering, the review queue fills with mood-driven
    orders, reviews get rubber-stamped, and Rule 8 stops protecting the
    orders it exists for.
    """
    assert requires_human_review([emotion]) is None, (
        f"{emotion!r} triggered review; it is sadness or mood, not bereavement"
    )


def test_trigger_reason_is_returned_not_just_a_bool() -> None:
    """The order's review_reason needs to name the word that caused it."""
    assert requires_human_review(["grieving my father"]) == "grief"
    assert requires_human_review(["joy", "remembrance"]) == "remembrance"


def test_empty_and_blank_input_is_safe() -> None:
    assert requires_human_review([]) is None
    assert requires_human_review(["", "   "]) is None


def test_mixed_profile_triggers_on_any_match() -> None:
    """One bereavement term in a profile is enough."""
    assert requires_human_review(["joy", "celebration", "loss"]) is not None


@pytest.mark.parametrize(
    "phrase",
    [
        "glossy foliage",       # contains "loss" as a substring
        "a memory of summer",   # the product's own input format
        "memories of her garden",
        "childhood memory",
        "lossless",
    ],
)
def test_substring_lookalikes_do_not_trigger(phrase: str) -> None:
    """The false-positive traps this domain actually contains.

    "glossy" contains "loss". "memory" is what every single customer submits
    -- CLAUDE.md describes the product as taking a memory as input -- so a
    bare memory token would flag every order ever placed and make the queue
    meaningless.
    """
    assert requires_human_review([phrase]) is None, f"{phrase!r} falsely triggered"


@pytest.mark.parametrize(
    "phrase", ["in memory of my mother", "in loving memory", "in memoriam"]
)
def test_commemorative_memory_phrasings_do_trigger(phrase: str) -> None:
    """The other side of that line: commemorative phrasing is not a mood."""
    assert requires_human_review([phrase]) == "in-memory"


def test_every_trigger_term_has_a_stem_defined() -> None:
    """No term may sit in the set with no way to match it."""
    from backend.config import _REVIEW_PHRASES, _REVIEW_STEMS

    covered = set(_REVIEW_STEMS) | set(_REVIEW_PHRASES)
    missing = sorted(REVIEW_REQUIRED_EMOTIONS - covered)
    assert not missing, f"trigger terms with no stem or phrase defined: {missing}"
