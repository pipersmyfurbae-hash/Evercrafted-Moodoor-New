# 36_REACT_COMPONENT_HIERARCHY

## Purpose

This document defines the React component hierarchy for Evercrafted Studio MVP.

---

## App Root

```text
RootLayout
├── AuthProvider
├── QueryClientProvider
├── WorkspaceProvider
└── AppShell
```

---

## AppShell

```text
AppShell
├── Sidebar
├── TopBar
└── PageContainer
```

---

## Dashboard

```text
DashboardPage
├── WelcomePanel
├── QuickActions
├── RecentBlueprints
└── SystemStatusCards
```

---

## Memory Weaver

```text
MemoryWeaverPage
├── MemoryInputForm
├── EmotionResultPanel
├── FormulaRecommendationCard
├── PaletteDirectionCard
└── CreateBlueprintButton
```

---

## Design Studio

```text
DesignStudioPage
├── StudioProvider
├── StudioHeader
├── StudioLayout
│   ├── StudioLeftPanel
│   │   ├── FormulaSummary
│   │   ├── LayerControls
│   │   ├── OverlayControls
│   │   └── BlueprintActions
│   ├── CanvasStage
│   │   ├── PlacementVisualizer
│   │   ├── RadialGridOverlay
│   │   ├── ZoneOverlay
│   │   └── SelectionOverlay
│   └── StudioRightPanel
│       ├── PlacementInspector
│       ├── MaterialInspector
│       ├── BlueprintValidationPanel
│       └── BlueprintJsonViewer
└── StudioFooter
```

---

## Inventory Weaver

```text
InventoryPage
├── InventoryToolbar
├── InventoryItemForm
├── InventoryTable
├── MaterialRoleFilter
└── CostSummary
```

---

## Design Library

```text
DesignLibraryPage
├── LibraryToolbar
├── BlueprintSearch
├── BlueprintFilterBar
├── BlueprintGrid
│   └── BlueprintCard
└── EmptyLibraryState
```

---

## Build Sheet

```text
BuildSheetPage
├── BuildSheetHeader
├── MaterialCountTable
├── BuildStepList
├── QualityChecklist
└── PrintExportActions
```

---

## Render Studio

```text
RenderStudioPage
├── RenderModeSelector
├── BlueprintSummaryPanel
├── PromptOutputPanel
├── PromptControls
└── CopyExportActions
```

---

## Shared Components

```text
Button
Card
Panel
Badge
Tabs
Modal
JsonViewer
StatusIndicator
LoadingState
EmptyState
```

---

## State Ownership

### Server State

Owned by TanStack Query:
- blueprints
- inventory
- build sheets
- user data

### Client State

Owned by Zustand/StudioProvider:
- selected placement
- visible layers
- current editor mode
- overlay toggles
- unsaved draft edits

---

## Component Rule

Do not put engine logic inside visual UI components.

Engine logic belongs in:
- backend services
- shared utility modules
- dedicated placement/rendering libraries
