# 05_EC_CANON_V1_BLUEPRINT_SCHEMA

## Purpose

EC_CANON_V1 is the canonical data object for every Evercrafted design.

All engines compile into this object. All apps read from it.

## Top-Level Blueprint Object

```json
{
  "blueprint_id": "EC_000001",
  "version": "1.0.0",
  "name": "Quiet Shoreline Remembrance",
  "created_at": "2026-05-24T00:00:00Z",
  "created_by": "user_id",
  "base": {},
  "emotion": {},
  "formula": {},
  "dna": {},
  "zones": [],
  "anchors": [],
  "placements": [],
  "materials": [],
  "visualization": {},
  "manufacturing": {},
  "commerce": {},
  "scores": {},
  "metadata": {}
}
```

## Base Schema

```json
{
  "form_factor": "circular",
  "diameter_in": 24,
  "base_type": "grapevine",
  "base_visibility_percent": 22
}
```

## Emotion Schema

```json
{
  "primary_tone": "quiet gratitude",
  "valence": 0.2,
  "arousal": -0.4,
  "quadrant": "Cozy & Calm",
  "emotion_vector": {
    "calm": 0.8,
    "nostalgia": 0.7,
    "hope": 0.4,
    "joy": 0.2
  },
  "narrative_summary": "A restrained remembrance design with soft coastal calm."
}
```

## Formula Schema

```json
{
  "formula_id": "crescent_asymmetrical",
  "formula_name": "Asymmetrical Crescent",
  "arc_start_deg": 120,
  "arc_end_deg": 270,
  "negative_space_deg": 150,
  "flow_direction": "counterclockwise"
}
```

## DNA Schema

```json
{
  "cluster_count": 3,
  "density_profile": 0.58,
  "cluster_spread_deg": 65,
  "greenery_direction": "outward",
  "silhouette_bias": "organic",
  "focal_ratio": 0.22,
  "silence_arc": 45,
  "style_signature": "editorial"
}
```

## Placement Object

```json
{
  "placement_id": "pl_001",
  "material_id": "mat_peony_cream",
  "role": "focal",
  "layer": "focal_floral",
  "theta_deg": 215,
  "clock_position": "7:10",
  "radius_norm": 0.72,
  "radius_in": 8.6,
  "rotation_deg": -18,
  "scale": 1.0,
  "stem_direction": "tucked_upward",
  "z_index": 40,
  "cluster_id": "cluster_lower_left"
}
```

## Validation Rules

A valid EC_CANON_V1 object must include blueprint ID, base dimensions, emotion metadata, formula ID, DNA profile, placement array, visualization settings, and manufacturing object.

Placement must be deterministic and reproducible.
