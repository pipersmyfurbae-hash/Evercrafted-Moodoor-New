# 78_AI_MODEL_ORCHESTRATION

## Purpose

Defines how AI models should be used inside Evercrafted.

---

## Core Rule

AI interprets. Geometry places.

---

## AI Responsibilities

AI may handle:
- emotional interpretation
- narrative extraction
- product copy
- render prompt generation
- build step explanation
- marketplace listing writing

AI must not be solely responsible for:
- placement coordinates
- final geometry
- blueprint validation
- database writes without validation
- schema generation at runtime

---

## Recommended AI Calls

### Emotion Classification
Input:
- memory text
- season
- size

Output:
- strict JSON emotion object

### Render Prompt Generation
Input:
- blueprint
- mode

Output:
- prompt text

### Build Step Explanation
Input:
- blueprint
- placements
- material counts

Output:
- human-readable build steps

---

## Deterministic Services

These should be code, not AI:
- formula rules
- DNA derivation
- placement generation
- validation
- scoring calculations
- z-index sorting

---

## Model-Agnostic Design

Evercrafted should not depend on a single AI vendor.

All AI calls should go through backend service wrappers.
