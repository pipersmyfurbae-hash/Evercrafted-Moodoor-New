"""Blueprint Scoring & Repair Engine -- the quality gate.

Deterministic, and must never import the Anthropic SDK (enforced by
tests/tripwires/test_no_anthropic_sdk.py). Scores 6 dimensions at 0-20 each
for a 120 total; CLAUDE.md Rule 7 forbids packaging anything below 80.

KNOWN CONFLICT to resolve when this is implemented: dimension D6 awards 5
points for "no banned florals present (cherry blossom, pussy willow, twig
blossoms)". That exclusion was lifted -- floral-canon.json records the lift
and both species are live in the canon. Implementing D6 verbatim would dock
5 of 120 from legitimate designs and could push them under the 80 gate with
no explanation given to anyone.

SPRINT 5. Ground truth: blueprint-scoring-repair-engine/SKILL.md.
"""
