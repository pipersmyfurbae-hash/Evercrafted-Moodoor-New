# 74_FRONTEND_FILE_STRUCTURE

## Purpose

Defines the production frontend file structure for Evercrafted Studio MVP.

---

## Recommended Structure

```text
/apps/web
  /app
    /dashboard
    /memory-weaver
    /design-studio
      /[blueprintId]
    /inventory
    /library
    /build-sheets
      /[blueprintId]
    /render-studio
      /[blueprintId]
    /settings
    layout.tsx
    page.tsx

  /components
    /ui
      Button.tsx
      Card.tsx
      Panel.tsx
      Badge.tsx
      Tabs.tsx
      Modal.tsx
      JsonViewer.tsx
    /layout
      AppShell.tsx
      Sidebar.tsx
      TopBar.tsx
      PageContainer.tsx

  /features
    /memory-weaver
      MemoryInputForm.tsx
      EmotionResultPanel.tsx
      FormulaRecommendationCard.tsx
    /design-studio
      DesignStudioPage.tsx
      StudioLeftPanel.tsx
      StudioCanvasStage.tsx
      StudioRightPanel.tsx
      PlacementInspector.tsx
      LayerControls.tsx
      BlueprintJsonViewer.tsx
    /visualizer
      PlacementVisualizer.tsx
      RadialGridOverlay.tsx
      ZoneOverlay.tsx
      render-utils.ts
    /inventory
      InventoryTable.tsx
      InventoryItemForm.tsx
    /library
      BlueprintGrid.tsx
      BlueprintCard.tsx
    /buildbloom
      BuildSheetView.tsx
      MaterialCountTable.tsx
      BuildStepList.tsx
    /render-studio
      PromptOutputPanel.tsx
      RenderModeSelector.tsx

  /lib
    api-client.ts
    constants.ts
    validation.ts
    blueprint-utils.ts
    polar-utils.ts

  /stores
    studio-store.ts
    workspace-store.ts

  /services
    blueprint-service.ts
    emotion-service.ts
    placement-service.ts
    inventory-service.ts
    build-sheet-service.ts
    render-service.ts

  /types
    evercrafted.ts

  /styles
    globals.css
    tokens.css
```

---

## Key Rule

Do not put engine logic directly inside React UI components.

UI components should call services or shared utilities.
