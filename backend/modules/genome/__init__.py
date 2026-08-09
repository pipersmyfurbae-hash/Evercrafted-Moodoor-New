"""Wreath Genome System -- encode, mutate, breed.

Deterministic. Encodes a blueprint as a WGS1 genome string; version must be
checked before decoding.

KNOWN CONFLICT to resolve when this is implemented: references/breeding.md
strips cherry blossom, pussy willow and twig blossoms from any child genome,
and SKILL.md forbids them in any genome. That exclusion was lifted -- see the
note in backend/config.py.

SPRINT 5. Ground truth: wreath-genome-system/references/genome-spec.md,
mutation-ops.md, breeding.md.
"""
