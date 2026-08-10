# 28_ENGINE_LAYER_MAP

## Purpose

This file explains how every Evercrafted engine connects.

## Master Flow

```text
Memory / Mood / Inventory / Style Input
        ↓
Emotion Engine
        ↓
Formula Engine
        ↓
Wreath DNA Engine
        ↓
Placement Engine
        ↓
Placement Visualization Engine
        ↓
Blueprint Compiler
        ↓
EC_CANON_V1 Blueprint
        ↓
BuildBloom / Design Studio / Render Studio / Design Library / Marketplace / Moodoor
```

## Engine Responsibilities

Emotion Engine understands feeling. Formula Engine chooses structural archetype. Wreath DNA Engine creates procedural trait profile. Placement Engine calculates deterministic geometry. Placement Visualization Engine shows the geometry. Blueprint Compiler turns outputs into canonical data. BuildBloom turns blueprint into real-world construction. Inventory Engine constrains and informs material choices.

## What Connects to What

Memory Weaver uses Emotion Engine, Formula Engine, and Blueprint Compiler.

Design Studio uses Placement Engine, Placement Visualization Engine, Blueprint Compiler, and Design Library.

Inventory Weaver uses Inventory Engine, Blueprint Compiler, and BuildBloom.

Render Studio uses EC_CANON_V1, formula, placement, and emotional metadata.

BuildBloom uses placements, materials, formula, base size, and manufacturing schema.

Moodoor uses Emotion Engine, Inventory Engine, match logic, and product blueprint metadata.

## Key Clarification

The engine is not separate from the product. The engine powers every product surface. The Studio is the usable creator interface. Moodoor is the consumer-facing emotional shopping interface. The Console is the internal operating interface.
