"""Golden fixtures.

Every SKU here is a real entry in floral-canon.json, verified by
tests/tripwires/test_sku_resolution.py. Nothing in this file may be
invented -- a fixture with a made-up SKU would make the tripwire that
guards Rule 2 pass against fiction.

Sprint 7 grows this to 15-20 briefs spanning grief, joy, peace and
celebration. Sprint 0 needs one of each shape.
"""

from __future__ import annotations

from backend.schemas.blueprint import (
    Cluster,
    Element,
    EmotionProfile,
    Position,
    WreathBlueprint,
)
from backend.schemas.enums import (
    LAYER_ORDER,
    BlueprintType,
    CompositionFormula,
    ElementCategory,
    Radius,
    Season,
)

# Real SKUs, read out of the canon.
SKU_GARDEN_ROSE = "98093.DCO"
SKU_RANUNCULUS = "98071.AB"
SKU_PEONY = "06079.PK"
SKU_EUCALYPTUS = "98883.GR"
SKU_DUSTY_MILLER = "95444.GY"
SKU_WAX_FLOWER = "06143.WH"
SKU_OLIVE = "95293.BKGR"

REAL_SKUS = (
    SKU_GARDEN_ROSE,
    SKU_RANUNCULUS,
    SKU_PEONY,
    SKU_EUCALYPTUS,
    SKU_DUSTY_MILLER,
    SKU_WAX_FLOWER,
    SKU_OLIVE,
)

# Deliberately absent from the canon. Used to prove the resolver rejects
# rather than silently substitutes.
FAKE_SKU = "99999.NOPE"

GOLDEN_SEED = 20260809
GOLDEN_BRIEF_FINGERPRINT = "sha256:golden-fixture-brief-0001"


def golden_blueprint(seed: int = GOLDEN_SEED) -> WreathBlueprint:
    """A structurally valid blueprint: 3 focal clusters, odd count, real SKUs.

    Not the output of the pipeline -- the pipeline does not exist yet. This
    is a hand-built specimen of the target shape, so the schema and the
    tripwires have something concrete to bite on before Sprint 1.
    """
    return WreathBlueprint(
        blueprint_id="BP-GOLDEN-0001",
        creator_id="CR-EVERCRAFTED-0001",
        blueprint_type=BlueprintType.SHELL,
        seed=seed,
        brief_fingerprint=GOLDEN_BRIEF_FINGERPRINT,
        wreath_size_inches=24,
        formula=CompositionFormula.CRESCENT,
        season=Season.EVERGREEN,
        emotion_profile=EmotionProfile(
            dominant_emotions=["warmth", "nostalgia"],
            design_intent="A kitchen door in late afternoon, the year the garden finally took.",
            intensity=6,
        ),
        layer_order=list(LAYER_ORDER),
        clusters=[
            Cluster(
                cluster_id="C1",
                position=Position(angle_deg=228.0, radius=Radius.OUTER),
                elements=[
                    Element(
                        sku=SKU_GARDEN_ROSE,
                        name="Rose Bud Pick 21.5in",
                        category=ElementCategory.FOCAL,
                        quantity=5,
                        emotion_tags=["warmth", "nostalgia"],
                    ),
                    Element(
                        sku=SKU_PEONY,
                        name="Peony 27in",
                        category=ElementCategory.FOCAL,
                        quantity=3,
                        emotion_tags=["warmth"],
                    ),
                ],
            ),
            Cluster(
                cluster_id="C2",
                position=Position(angle_deg=274.0, radius=Radius.MID),
                elements=[
                    Element(
                        sku=SKU_RANUNCULUS,
                        name="Ranunculus 18.5in",
                        category=ElementCategory.FOCAL,
                        quantity=4,
                        emotion_tags=["nostalgia", "tender"],
                    ),
                    Element(
                        sku=SKU_WAX_FLOWER,
                        name="Wax Flower 26in White",
                        category=ElementCategory.FILLER,
                        quantity=6,
                        emotion_tags=["tender"],
                    ),
                ],
            ),
            Cluster(
                cluster_id="C3",
                position=Position(angle_deg=316.0, radius=Radius.INNER),
                elements=[
                    Element(
                        sku=SKU_EUCALYPTUS,
                        name="Long Eucalyptus w/ Pod Stem 30in",
                        category=ElementCategory.FOCAL,
                        quantity=3,
                        emotion_tags=["peace"],
                    ),
                    Element(
                        sku=SKU_DUSTY_MILLER,
                        name="Dusty Miller Spray 26.5in",
                        category=ElementCategory.SECONDARY,
                        quantity=4,
                        emotion_tags=["nostalgia"],
                    ),
                    Element(
                        sku=SKU_OLIVE,
                        name="Olive Leaf Branch 38in",
                        category=ElementCategory.GREENERY,
                        quantity=7,
                        emotion_tags=["peace", "warmth"],
                    ),
                ],
            ),
        ],
    )
