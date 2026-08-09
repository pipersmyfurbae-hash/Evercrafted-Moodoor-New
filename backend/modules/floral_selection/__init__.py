"""Floral selection -- emotion and colour negotiated against real stock.

Deterministic. The three-phase algorithm (emotion candidates -> colour filter
-> fallback -> season/intensity weighting) is scored code, not model output,
because Rule 6 requires the same brief to select the same florals every time.

`canon.py` is the single reader of floral-canon.json and the only place a SKU
is resolved (CLAUDE.md Rule 2).

SPRINT 3. Ground truth: evercrafted-floral-selector/references/
emotion-wheel-taxonomy.md and color-emotion-map.md.
"""
