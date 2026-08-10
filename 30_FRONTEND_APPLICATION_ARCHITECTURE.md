# 30_FRONTEND_APPLICATION_ARCHITECTURE

## Purpose

This document defines the frontend architecture for the Evercrafted MVP.

It translates the canon, engine layer, and Design Studio product requirements into an implementable React/Next.js application structure.

---

## Product Surface

The MVP frontend is Evercrafted Studio.

It should not expose the full Evercrafted OS complexity to normal users. The OS concepts power the product, but the Studio UI should feel creator-friendly, premium, structured, and understandable.

---

## Recommended Frontend Stack

- Next.js App Router
- React
- TypeScript
- Tailwind CSS or tokenized CSS
- Zustand for client-side workspace state
- TanStack Query for API data fetching
- React Hook Form for forms
- Canvas or SVG for Placement Visualization Engine

---

## Application Shell

The app should use a persistent shell:

```text
<AppShell>
  <SidebarNavigation />
  <TopBar />
  <MainWorkspace />
</AppShell>
```

### Sidebar Navigation

MVP navigation:
- Dashboard
- Memory Weaver
- Design Studio
- Inventory Weaver
- Design Library
- Build Sheets
- Render Studio
- Settings

### Top Bar

Top bar should show:
- current workspace
- active blueprint name
- save status
- export/action buttons where relevant

---

## Route Structure

Recommended MVP routes:

```text
/app
/app/dashboard
/app/memory-weaver
/app/design-studio
/app/design-studio/[blueprintId]
/app/inventory
/app/library
/app/library/[blueprintId]
/app/build-sheets/[blueprintId]
/app/render-studio/[blueprintId]
/app/settings
```

---

## Frontend Domains

### 1. Workspace Domain

Owns:
- active blueprint
- active project/session
- selected material
- current tool mode
- save state

### 2. Blueprint Domain

Owns:
- EC_CANON_V1 object
- placement data
- blueprint validation
- version state

### 3. Visualizer Domain

Owns:
- canvas/SVG render state
- zoom/pan
- visible layers
- selected placement
- overlays

### 4. Inventory Domain

Owns:
- material list
- availability
- costs
- material roles

### 5. BuildBloom Domain

Owns:
- generated build sheet
- step sequence
- material counts

---

## State Management

Use API as source of truth for saved data.

Use Zustand or equivalent for active editing state:

```ts
type StudioState = {
  activeBlueprintId?: string;
  draftBlueprint?: Blueprint;
  selectedPlacementId?: string;
  visibleLayers: string[];
  showRadialGrid: boolean;
  showZones: boolean;
  editorMode: "view" | "edit" | "inspect";
};
```

---

## API Fetching

Use TanStack Query for:
- blueprints
- inventory
- build sheets
- render prompts
- user/account data

Use mutations for:
- compile blueprint
- save blueprint
- generate placement
- update inventory
- generate build sheet

---

## MVP Page Responsibilities

### Dashboard

Purpose:
- simple product entry point
- recent designs
- quick action buttons

### Memory Weaver

Purpose:
- emotional intake
- concept generation
- blueprint creation

Must connect to:
- Emotion Engine
- Formula Engine
- Blueprint Compiler

### Design Studio

Purpose:
- main editor
- visualize placement
- inspect blueprint
- save/export

Must connect to:
- Placement Engine
- Placement Visualization Engine
- Blueprint Compiler
- Design Library

### Inventory Weaver

Purpose:
- material entry
- role assignment
- cost management

### Design Library

Purpose:
- saved blueprint listing
- open/duplicate/export

### Build Sheet Page

Purpose:
- BuildBloom output view
- printable manufacturing steps

### Render Studio

Purpose:
- generate image prompts and listing visual direction from blueprint

---

## Frontend Rules

- Do not call AI APIs directly from frontend.
- Do not generate final placement client-side unless using approved deterministic utility shared with backend.
- Do not store canonical data only in browser local state.
- Do not make Design Studio dependent on image generation.
- Keep visualizer functional with placeholder material icons/dots if asset images are unavailable.

---

## MVP Completion Definition

Frontend MVP is complete when the user can:

1. Enter a Memory Weaver prompt.
2. Generate a blueprint.
3. Open it in Design Studio.
4. See deterministic placement preview.
5. Inspect placement data.
6. Save to library.
7. Generate a BuildBloom build sheet.
