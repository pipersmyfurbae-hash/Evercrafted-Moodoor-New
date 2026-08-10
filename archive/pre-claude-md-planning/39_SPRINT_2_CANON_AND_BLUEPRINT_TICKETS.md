# 39_SPRINT_2_CANON_AND_BLUEPRINT_TICKETS

## Sprint Goal

Implement EC_CANON_V1 blueprint persistence and CRUD foundations.

This sprint creates the first real Evercrafted data flow:
- create blueprint
- save blueprint
- load blueprint
- list blueprints

This is infrastructure and data architecture.

This sprint is NOT:
- visual design
- placement generation
- Memory Weaver logic
- marketplace
- Moodoor

---

# Ticket 2.1 — Blueprint Schema Alignment

## Goal

Align backend and frontend around EC_CANON_V1 blueprint structure.

## Requirements

- Shared Blueprint type used consistently
- Backend accepts EC_CANON_V1 payload
- Blueprint validation structure exists

## Acceptance Criteria

- Blueprint schema_version locked to EC_CANON_V1
- Shared type imports work
- Invalid blueprint payload rejected

---

# Ticket 2.2 — Blueprint CRUD API

## Goal

Create foundational blueprint API routes.

## Required Routes

- POST /api/v1/blueprints
- GET /api/v1/blueprints
- GET /api/v1/blueprints/:id

## Acceptance Criteria

- Blueprint can be created
- Blueprint can be fetched
- Blueprint list returns array
- Stable JSON response shape

---

# Ticket 2.3 — In-Memory Blueprint Storage

## Goal

Create temporary persistence layer before real DB integration.

## Acceptance Criteria

- Blueprint storage service exists
- Create/read/list operations work
- Uses deterministic IDs
- Service isolated from API layer

---

# Ticket 2.4 — Frontend Blueprint Test Page

## Goal

Create minimal test page to verify blueprint flow.

## Acceptance Criteria

- User can submit test blueprint
- Frontend calls backend successfully
- Blueprint list renders
- No polished UI required

---

# Ticket 2.5 — Shared Validation Rules

## Goal

Prevent schema drift between frontend/backend.

## Acceptance Criteria

- Shared validation structure exists
- Backend validates required fields
- Invalid schema_version rejected
- Missing fields rejected

---

# Important Rule

Do NOT build:
- Design Studio
- placement engine
- visualizer
- Memory Weaver UI
- Marketplace
- Moodoor
- authentication
- polished dashboards