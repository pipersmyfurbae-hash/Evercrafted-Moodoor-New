# 89_SINGLE_SOURCE_OF_TRUTH_GUIDE

## Purpose

This file explains which documents are the source of truth for each type of decision.

---

# Product Scope

Source of truth:
- `03_EVERCRAFTED_MVP_SCOPE.md`
- `35_MVP_ACCEPTANCE_CRITERIA.md`
- `86_DO_NOT_BUILD_YET_LIST.md`

---

# Architecture

Source of truth:
- `04_EVERCRAFTED_SYSTEM_ARCHITECTURE.md`
- `28_ENGINE_LAYER_MAP.md`
- `30_FRONTEND_APPLICATION_ARCHITECTURE.md`
- `31_BACKEND_SERVICE_ARCHITECTURE.md`

---

# Blueprint Schema

Source of truth:
- `05_EC_CANON_V1_BLUEPRINT_SCHEMA.md`
- `73_TYPESCRIPT_SHARED_TYPES.ts`

---

# API

Source of truth:
- `20_API_CONTRACTS.md`
- `72_API_OPENAPI_SPEC.yaml`

---

# Database

Source of truth:
- `21_DATABASE_SCHEMA.md`
- `71_DATABASE_TABLE_DEFINITIONS.sql`

---

# Placement

Source of truth:
- `09_PLACEMENT_ENGINE_SPEC.md`
- `29_PROCEDURAL_PLACEMENT_DOCTRINE.md`

---

# Visualizer

Source of truth:
- `10_PLACEMENT_VISUALIZATION_ENGINE_SPEC.md`
- `33_VISUALIZER_RENDER_PIPELINE.md`

---

# Design Studio

Source of truth:
- `15_DESIGN_STUDIO_PRD.md`
- `32_DESIGN_STUDIO_COMPONENT_MAP.md`
- `36_REACT_COMPONENT_HIERARCHY.md`

---

# Build Order

Source of truth:
- `22_MVP_SPRINT_PLAN.md`
- `38–44 sprint ticket files`
- `85_MVP_BUILD_ORDER_CHECKLIST.md`

---

# Brand / Canon

Source of truth:
- `00_EVERCRAFTED_UNIFIED_ECOSYSTEM_CANON.md`
- `01_EVERCRAFTED_MASTER_CANON.md`
- `70_EVERCRAFTED_MASTER_CONSTITUTION.md`

---

# Rule

When documents conflict, use the most execution-specific document for build decisions.

Example:
- If vision file says “Marketplace matters”
- but MVP scope says “Do not build Marketplace”
- MVP scope wins for current build.
