"""Seeded deterministic RNG for the placement engine.

mulberry32 -- the generator the roadmap names for Sprint 4. It exists in
Sprint 0 because the same-seed-same-output tripwire needs a real seeded
surface to test; a tripwire written against a hardcoded constant passes
forever and guards nothing.

Deliberately not `random.Random`: Python's Mersenne Twister carries no
cross-language guarantee, and a blueprint seed may eventually need to
reproduce identically in the TypeScript frontend. mulberry32 is a fixed
32-bit integer algorithm that produces the same stream anywhere.

Contains no AI calls. This module must never import the Anthropic SDK
(CLAUDE.md Rule 1, enforced by tests/tripwires/test_no_anthropic_sdk.py).
"""

from __future__ import annotations

_UINT32 = 0xFFFFFFFF


class Mulberry32:
    """A seeded PRNG producing an identical stream for an identical seed.

    >>> a = Mulberry32(42)
    >>> b = Mulberry32(42)
    >>> [a.next_float() for _ in range(3)] == [b.next_float() for _ in range(3)]
    True
    """

    __slots__ = ("_state", "_seed")

    def __init__(self, seed: int) -> None:
        if not 0 <= seed <= _UINT32:
            raise ValueError(f"seed {seed} out of uint32 range")
        self._seed = seed
        self._state = seed

    @property
    def seed(self) -> int:
        return self._seed

    def next_uint32(self) -> int:
        self._state = (self._state + 0x6D2B79F5) & _UINT32
        z = self._state
        z = ((z ^ (z >> 15)) * (z | 1)) & _UINT32
        z ^= (z + ((z ^ (z >> 7)) * (z | 61)) & _UINT32) & _UINT32
        z &= _UINT32
        return (z ^ (z >> 14)) & _UINT32

    def next_float(self) -> float:
        """Uniform in [0, 1)."""
        return self.next_uint32() / 4294967296.0

    def uniform(self, low: float, high: float) -> float:
        if high < low:
            raise ValueError(f"uniform({low}, {high}): high < low")
        return low + (high - low) * self.next_float()

    def randint(self, low: int, high: int) -> int:
        """Inclusive on both ends."""
        if high < low:
            raise ValueError(f"randint({low}, {high}): high < low")
        return low + int(self.next_float() * (high - low + 1))

    def choice(self, items):
        seq = list(items)
        if not seq:
            raise ValueError("choice() on an empty sequence")
        return seq[self.randint(0, len(seq) - 1)]

    def reset(self) -> None:
        self._state = self._seed
