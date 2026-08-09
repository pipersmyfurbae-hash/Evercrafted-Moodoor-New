"""Versioned blueprint contract.

This is the artifact every module reads or writes, so it lives outside
`modules/` -- a shared contract is not a module, and modules are forbidden
from importing each other (CLAUDE.md, "Repo Structure").

Field shape follows blueprint-scoring-repair-engine/SKILL.md, which defines
the minimum input the quality gate accepts. Anything the gate reads is
required here so a blueprint cannot reach scoring structurally incapable of
being scored.
"""

from __future__ import annotations

import json
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from backend.config import BLUEPRINT_SCHEMA_VERSION, MAX_BLUEPRINT_SCORE
from backend.schemas.enums import (
    VALID_FOCAL_CLUSTER_COUNTS,
    BlueprintStatus,
    BlueprintType,
    CompositionFormula,
    ElementCategory,
    Radius,
    Season,
    Symmetry,
)


class _Base(BaseModel):
    """Strict by default.

    `extra="forbid"` is deliberate: a typo'd field name should fail loudly at
    the module boundary rather than being silently dropped and reappearing as
    a missing-data bug three stages downstream.
    """

    model_config = ConfigDict(extra="forbid", frozen=False, use_enum_values=False)


class EmotionProfile(_Base):
    """The one part of a blueprint an LLM is allowed to author.

    Text and tags only -- never coordinates, angles, or radii (Rule 1).
    """

    dominant_emotions: list[str] = Field(default_factory=list)
    design_intent: str = ""
    atmosphere: str | None = None
    movement: str | None = None
    intensity: int | None = Field(default=None, ge=1, le=10)


class Position(_Base):
    """Where a cluster sits. Emitted only by the placement engine (Rule 1)."""

    angle_deg: float = Field(ge=0.0, lt=360.0)
    radius: Radius

    @property
    def quadrant(self) -> str:
        """Q1 0-90 (12->3 o'clock), Q2 90-180, Q3 180-270, Q4 270-360.

        Matches the quadrant map in blueprint-scoring-repair-engine D2.
        """
        return f"Q{int(self.angle_deg // 90) + 1}"


class Element(_Base):
    """A single stem placement.

    `sku` must resolve against the floral canon -- enforced by the SKU
    tripwire, not by this model, because resolution needs the canon loaded
    and a schema should not do I/O.
    """

    sku: str = Field(min_length=1)
    name: str = Field(min_length=1)
    category: ElementCategory
    quantity: int = Field(ge=1)
    emotion_tags: list[str] = Field(default_factory=list)


class Cluster(_Base):
    cluster_id: str = Field(min_length=1)
    position: Position
    elements: list[Element] = Field(min_length=1)

    @property
    def element_count(self) -> int:
        return sum(e.quantity for e in self.elements)

    @property
    def is_focal(self) -> bool:
        return any(e.category is ElementCategory.FOCAL for e in self.elements)


class ScoreReport(_Base):
    """Output of the 6-dimension quality gate. Populated in Sprint 5."""

    overall_score: int = Field(ge=0, le=MAX_BLUEPRINT_SCORE)
    dimension_scores: dict[str, int] = Field(default_factory=dict)
    critical_flags: list[str] = Field(default_factory=list)
    engine_version: str = "BSRE-1.0"

    @field_validator("dimension_scores")
    @classmethod
    def _dimensions_in_range(cls, v: dict[str, int]) -> dict[str, int]:
        for name, score in v.items():
            if not 0 <= score <= 20:
                raise ValueError(f"dimension {name} scored {score}, must be 0-20")
        return v


class WreathBlueprint(_Base):
    """The full blueprint contract.

    Determinism note: `seed` and `brief_fingerprint` together are the inputs
    that Rule 6 promises are reproducible. Two blueprints sharing both must
    serialize byte-identically via `canonical_json()`.
    """

    schema_version: Literal["EC_WR_V2"] = BLUEPRINT_SCHEMA_VERSION

    blueprint_id: str = Field(min_length=1)
    creator_id: str = Field(min_length=1)
    blueprint_type: BlueprintType = BlueprintType.SHELL
    status: BlueprintStatus = BlueprintStatus.DRAFT

    seed: int = Field(ge=0, le=2**32 - 1)
    brief_fingerprint: str = Field(min_length=1)

    wreath_size_inches: int = Field(ge=12, le=36)
    formula: CompositionFormula
    season: Season | None = None
    symmetry: Symmetry = Symmetry.ASYMMETRIC

    emotion_profile: EmotionProfile = Field(default_factory=EmotionProfile)
    clusters: list[Cluster] = Field(default_factory=list)
    layer_order: list[ElementCategory] = Field(default_factory=list)

    genome: str | None = None
    score: ScoreReport | None = None
    preview_url: str | None = None

    @field_validator("clusters")
    @classmethod
    def _odd_focal_cluster_count(cls, clusters: list[Cluster]) -> list[Cluster]:
        """CLAUDE.md Rule 4 -- odd focal cluster counts only (3, 5, or 7).

        Counts focal clusters, not all clusters: accent and filler satellites
        are unconstrained. An empty cluster list is allowed so that a draft
        blueprint can exist before placement runs.
        """
        focal = [c for c in clusters if c.is_focal]
        if focal and len(focal) not in VALID_FOCAL_CLUSTER_COUNTS:
            raise ValueError(
                f"{len(focal)} focal clusters; must be one of "
                f"{sorted(VALID_FOCAL_CLUSTER_COUNTS)} (CLAUDE.md Rule 4)"
            )
        return clusters

    @model_validator(mode="after")
    def _cluster_ids_unique(self) -> WreathBlueprint:
        ids = [c.cluster_id for c in self.clusters]
        if len(ids) != len(set(ids)):
            dupes = sorted({i for i in ids if ids.count(i) > 1})
            raise ValueError(f"duplicate cluster_id(s): {dupes}")
        return self

    @property
    def total_stems(self) -> int:
        return sum(c.element_count for c in self.clusters)

    @property
    def skus(self) -> list[str]:
        """Every SKU referenced, in stable order. Read by the SKU tripwire."""
        return sorted({e.sku for c in self.clusters for e in c.elements})

    def quadrant_mass(self) -> dict[str, int]:
        """Element count per quadrant, derived rather than stored.

        The scoring engine says to calculate this from cluster positions when
        absent; deriving it always removes the chance of a stored copy going
        stale after a repair rotates a cluster.
        """
        mass = {"Q1": 0, "Q2": 0, "Q3": 0, "Q4": 0}
        for cluster in self.clusters:
            mass[cluster.position.quadrant] += cluster.element_count
        return mass

    def canonical_json(self) -> str:
        """Deterministic serialization for the same-seed tripwire.

        Sorted keys and fixed separators, so a byte comparison tests the
        blueprint's content rather than dict ordering or float formatting.
        """
        payload: Any = self.model_dump(mode="json")
        return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
