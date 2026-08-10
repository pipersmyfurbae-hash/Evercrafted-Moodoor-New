"""The 7 pipeline endpoints, plus the supporting status route.

CONTRACT STUB. Every route below declares its real request and response
shape and returns 501. The shapes are the Sprint 0 deliverable -- Design
wires Phase 3 concepts to this contract, and the sprints that follow fill in
the bodies without changing the signatures.

Route names are transcribed from CLAUDE.md's "API Contract -- The 7 Pipeline
Endpoints (canonical list)". They are not to be renamed here: if one needs to
change, CLAUDE.md changes first, then this file.

Ownership, per that table:
    1  /api/intake          Sprint 2   Client Design Intake Engine
    2  /api/emotion-profile Sprint 2   Emotional Design Translator      [AI]
    3  /api/floral-select   Sprint 3   Evercrafted Floral Selector
    4  /api/place           Sprint 4   Placement Intelligence Engine
    5  /api/story           Sprint 5   Story Genesis, marketplace mode  [AI]
    6  /api/generate-pdf    Sprint 5-6a Composition + Scoring + Genome +
                                       Builder Instructions + PDF render
    7  /api/listing         Sprint 6a  Marketplace Creator + Etsy Listing [AI]
    -  GET /api/blueprints/{id}  Sprint 1  status polling / result fetch
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from backend.api.schemas import (
    BlueprintStatusResponse,
    BriefRequest,
    EmotionProfileResponse,
    ErrorResponse,
    FloralSelectResponse,
    GeneratePdfResponse,
    IntakeRequest,
    IntakeResponse,
    ListingRequest,
    ListingResponse,
    PlacementRequest,
    PlacementResponse,
    StoryResponse,
)

router = APIRouter(prefix="/api", tags=["pipeline"])

_RESPONSES: dict[int | str, dict] = {
    501: {"model": ErrorResponse, "description": "Not implemented yet"},
}


def _not_implemented(route: str, sprint: str) -> None:
    """A stub must fail loudly and say when it will not.

    501 rather than a fabricated payload: a client that gets plausible fake
    data cannot tell a stub from a working endpoint, and Design would build
    against fiction.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=f"{route} is a Sprint 0 contract stub; implementation lands in {sprint}.",
    )


@router.post(
    "/intake",
    response_model=IntakeResponse,
    status_code=status.HTTP_201_CREATED,
    responses=_RESPONSES,
    summary="Step 1 — normalize a raw customer brief",
)
def intake(payload: IntakeRequest) -> IntakeResponse:
    _not_implemented("POST /api/intake", "Sprint 2")


@router.post(
    "/emotion-profile",
    response_model=EmotionProfileResponse,
    responses=_RESPONSES,
    summary="Step 2 — translate a brief into an emotional profile",
    description=(
        "One of exactly three AI touchpoints. Returns text and JSON tags "
        "only; never coordinates, angles, or radii (Rule 1). Flags "
        "bereavement profiles for human review (Rule 8)."
    ),
)
def emotion_profile(payload: BriefRequest) -> EmotionProfileResponse:
    _not_implemented("POST /api/emotion-profile", "Sprint 2")


@router.post(
    "/floral-select",
    response_model=FloralSelectResponse,
    responses=_RESPONSES,
    summary="Step 3 — rank real in-stock florals for the brief",
    description=(
        "Every returned SKU resolves against floral-canon.json. Emotions "
        "with no carrier in stock are reported in `unmatched_emotions` "
        "rather than filled with a substitute (Rule 2)."
    ),
)
def floral_select(payload: BriefRequest) -> FloralSelectResponse:
    _not_implemented("POST /api/floral-select", "Sprint 3")


@router.post(
    "/place",
    response_model=PlacementResponse,
    responses=_RESPONSES,
    summary="Step 4 — deterministic placement geometry + validation report",
    description=(
        "Pure deterministic geometry from R1-R18. No AI involvement (Rule "
        "1). The same seed and brief always produce identical placements "
        "(Rule 6)."
    ),
)
def place(payload: PlacementRequest) -> PlacementResponse:
    _not_implemented("POST /api/place", "Sprint 4")


@router.post(
    "/story",
    response_model=StoryResponse,
    responses=_RESPONSES,
    summary="Step 5 — marketplace-mode story text",
    description=(
        "AI touchpoint, text only. Marketplace mode is the shorter Level 1 "
        "output, not the 600-800 word cinematic arc. Subject to the Rule 10 "
        "adjective ban."
    ),
)
def story(payload: BriefRequest) -> StoryResponse:
    _not_implemented("POST /api/story", "Sprint 5")


@router.post(
    "/generate-pdf",
    response_model=GeneratePdfResponse,
    responses=_RESPONSES,
    summary="Step 6 — assemble, score, encode, and render the PDF bundle",
    description=(
        "Owns several internal sub-stages -- composition, scoring and "
        "repair, genome encoding, builder instructions, PDF render. They "
        "are not separate customer-facing steps, so they get no separate "
        "routes."
    ),
)
def generate_pdf(payload: BriefRequest) -> GeneratePdfResponse:
    _not_implemented("POST /api/generate-pdf", "Sprint 5-6a")


@router.post(
    "/listing",
    response_model=ListingResponse,
    responses=_RESPONSES,
    summary="Step 7 — marketplace listing copy + checkout link",
    description=(
        "Refuses to package a blueprint scoring below 80/120 (Rule 7). "
        "Listing copy is an AI touchpoint, text only."
    ),
)
def listing(payload: ListingRequest) -> ListingResponse:
    _not_implemented("POST /api/listing", "Sprint 6a")


@router.get(
    "/blueprints/{blueprint_id}",
    response_model=BlueprintStatusResponse,
    responses={**_RESPONSES, 404: {"model": ErrorResponse}},
    summary="Supporting — poll status / fetch result",
    description=(
        "Not one of the 7 pipeline stages, but required for the walking "
        "skeleton and named in CLAUDE.md's Definition-of-Done convention."
    ),
)
def get_blueprint(blueprint_id: str) -> BlueprintStatusResponse:
    _not_implemented(f"GET /api/blueprints/{blueprint_id}", "Sprint 1")
