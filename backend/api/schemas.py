"""Request and response models for the 7 pipeline endpoints.

These define the contract Design wires its Phase 3 concepts to, so the shapes
here are the deliverable -- not the (absent) logic behind them. Route names
come from CLAUDE.md's "API Contract -- The 7 Pipeline Endpoints (canonical
list)" and are not to be invented or renamed ad hoc: if one needs to change,
CLAUDE.md changes first.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from backend.schemas.blueprint import EmotionProfile, ScoreReport
from backend.schemas.enums import (
    BlueprintStatus,
    BlueprintType,
    CompositionFormula,
    Radius,
    Season,
)


class _Model(BaseModel):
    model_config = ConfigDict(extra="forbid")


# --- 1. POST /api/intake -------------------------------------------------


class IntakeRequest(_Model):
    """Raw customer input. Deliberately permissive -- normalization is the
    intake engine's job (Sprint 2), not the client's."""

    raw_input: str = Field(min_length=1, max_length=5000)
    customer_email: str | None = None
    wreath_size_inches: int = Field(default=24, ge=12, le=36)
    occasion: str | None = None
    season: Season | None = None


class NormalizedBrief(_Model):
    wreath_size_inches: int
    stem_count_target: int | None = None
    palette_60: str | None = None
    palette_30: str | None = None
    palette_10: str | None = None
    occasion: str | None = None
    season: Season | None = None


class IntakeResponse(_Model):
    brief_id: str
    fingerprint: str = Field(
        description="Stable hash of the normalized brief. With `seed`, the "
        "pair Rule 6 promises is reproducible."
    )
    normalized: NormalizedBrief


# --- 2. POST /api/emotion-profile ----------------------------------------


class BriefRequest(_Model):
    """Shared by stages 2-6: every one of them takes a brief_id."""

    brief_id: str = Field(min_length=1)


class EmotionProfileResponse(_Model):
    brief_id: str
    emotion_profile: EmotionProfile
    requires_human_review: bool = Field(
        description="True when the profile matches a bereavement trigger. "
        "CLAUDE.md Rule 8 -- such orders stop at pending_review and never "
        "auto-deliver."
    )
    review_reason: str | None = None


# --- 3. POST /api/floral-select ------------------------------------------


class FloralCandidate(_Model):
    """One ranked stem. `sku` always resolves against the floral canon --
    inventing one violates Rule 2."""

    sku: str
    name: str
    species: str
    role: str | None = None
    color_name: str | None = None
    price: float | None = None
    score: float = Field(ge=0.0, description="Selection score, higher ranks first")
    emotion_tags: list[str] = Field(default_factory=list)


class FloralSelectResponse(_Model):
    brief_id: str
    florals: list[FloralCandidate]
    unmatched_emotions: list[str] = Field(
        default_factory=list,
        description="Emotions with no carrier in stock. Rule 2 forbids "
        "substituting silently, so these are surfaced rather than filled.",
    )


# --- 4. POST /api/place --------------------------------------------------


class PlacementRequest(_Model):
    brief_id: str = Field(min_length=1)
    seed: int | None = Field(
        default=None,
        ge=0,
        le=2**32 - 1,
        description="Omit to derive from the brief fingerprint. Supplying it "
        "reproduces a previous run exactly (Rule 6).",
    )


class PlacementPosition(_Model):
    cluster_id: str
    angle_deg: float = Field(ge=0.0, lt=360.0)
    radius: Radius


class ValidationFinding(_Model):
    rule: str = Field(description="R-rule identifier, e.g. R7")
    level: str = Field(description="pass | warn | flag")
    detail: str


class PlacementResponse(_Model):
    brief_id: str
    seed: int
    formula: CompositionFormula
    placements: list[PlacementPosition]
    validation: list[ValidationFinding] = Field(default_factory=list)


# --- 5. POST /api/story --------------------------------------------------


class StoryResponse(_Model):
    brief_id: str
    story: str = Field(
        description="Marketplace-mode Level 1 output -- the shorter form, not "
        "the 600-800 word cinematic arc."
    )
    word_count: int


# --- 6. POST /api/generate-pdf -------------------------------------------


class GeneratePdfResponse(_Model):
    """One endpoint owning several internal sub-stages: composition, scoring
    and repair, genome encoding, builder instructions, and PDF render. They
    are not separate customer-facing steps, so they get no separate routes."""

    brief_id: str
    blueprint_id: str
    pdf_url: str | None = None
    genome: str | None = None
    score: ScoreReport | None = None


# --- 7. POST /api/listing ------------------------------------------------


class ListingRequest(_Model):
    """The one stage keyed on blueprint_id rather than brief_id."""

    blueprint_id: str = Field(min_length=1)
    blueprint_type: BlueprintType = BlueprintType.SHELL


class ListingResponse(_Model):
    blueprint_id: str
    title: str
    description: str
    tags: list[str] = Field(default_factory=list)
    price_usd: float = Field(ge=15.0, le=130.0)
    checkout_url: str | None = None


# --- supporting: GET /api/blueprints/{id} --------------------------------


class BlueprintStatusResponse(_Model):
    """Status polling and result fetch.

    Not one of the 7 pipeline stages, but required for the walking skeleton
    and named in CLAUDE.md's Definition-of-Done convention.
    """

    blueprint_id: str
    status: BlueprintStatus
    pdf_url: str | None = None
    preview_url: str | None = None
    score: int | None = None
    requires_human_review: bool = False


# --- errors --------------------------------------------------------------


class ErrorResponse(_Model):
    detail: str
    code: str | None = None
