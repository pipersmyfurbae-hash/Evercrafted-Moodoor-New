# 31_BACKEND_SERVICE_ARCHITECTURE

## Purpose

This document defines the backend service architecture for the Evercrafted MVP.

It explains how the engine layer becomes production infrastructure.

---

## Recommended Backend Stack

Option A:
- FastAPI
- Python
- PostgreSQL
- SQLAlchemy
- Alembic
- Redis/Celery later for async jobs

Option B:
- Node.js / TypeScript
- PostgreSQL
- Prisma
- BullMQ later for async jobs

Either is acceptable. The critical requirement is that all AI calls happen server-side.

---

## Core Services

### Auth Service

Responsibilities:
- user account
- session/JWT
- workspace ownership

### Emotion Service

Responsibilities:
- call AI model server-side
- return strict JSON
- classify memory/mood input
- derive valence/arousal/quadrant/vector

Endpoint:
```http
POST /api/v1/emotion/classify
```

### Formula Service

Responsibilities:
- map emotion output to formula
- apply formula rules
- return formula object

May be deterministic code, not AI.

### DNA Service

Responsibilities:
- derive procedural traits from emotion + formula
- return DNA object

Should be deterministic.

### Placement Service

Responsibilities:
- generate polar coordinates
- assign zones/clusters/layers
- enforce spacing
- assign z-index
- validate geometry

Endpoint:
```http
POST /api/v1/placement/generate
```

### Blueprint Compiler Service

Responsibilities:
- normalize all outputs into EC_CANON_V1
- validate required fields
- persist blueprint if requested

Endpoint:
```http
POST /api/v1/blueprints/compile
```

### Inventory Service

Responsibilities:
- CRUD inventory
- material roles
- availability
- costs
- material selection

### BuildBloom Service

Responsibilities:
- generate material counts
- build sequence
- assembly instructions
- printable build sheet object

Endpoint:
```http
POST /api/v1/build-sheet/generate
```

### Render Prompt Service

Responsibilities:
- generate render prompt from blueprint
- produce product photo direction
- preserve faux floral realism

Endpoint:
```http
POST /api/v1/render-prompt/generate
```

---

## Backend Flow: Memory to Blueprint

```text
POST /emotion/classify
  ↓
Formula Service
  ↓
DNA Service
  ↓
Placement Service
  ↓
Blueprint Compiler
  ↓
Save Blueprint
  ↓
Return EC_CANON_V1
```

---

## AI Boundary

AI may be used for:
- emotion interpretation
- narrative summary
- render prompts
- product copy
- build step explanation

AI must not be the sole source of:
- placement geometry
- spacing
- z-index
- schema validation
- database structure

---

## Validation Layer

Every blueprint save must validate:
- valid user ownership
- required EC_CANON_V1 fields
- valid placements
- valid material roles
- valid base size
- valid formula
- no malformed JSON

---

## Suggested Folder Structure

```text
/backend
  /app
    /api
      /routes
    /services
      emotion_service.py
      formula_service.py
      dna_service.py
      placement_service.py
      blueprint_compiler.py
      inventory_service.py
      buildbloom_service.py
      render_prompt_service.py
    /models
    /schemas
    /db
    /core
```

---

## MVP Backend Acceptance Criteria

Backend is MVP-ready when:

1. User can authenticate.
2. Emotion endpoint returns strict structured JSON.
3. Placement endpoint returns deterministic placement array.
4. Blueprint compiler returns valid EC_CANON_V1.
5. Blueprints can be saved and loaded.
6. Inventory items can be created and attached to blueprints.
7. BuildBloom generates build sheet JSON.
