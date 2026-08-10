# 04_EVERCRAFTED_SYSTEM_ARCHITECTURE

## Purpose

This document defines the architecture of Evercrafted across OS, Studio, and Moodoor.

It explains how the engine, visualizer, blueprint system, apps, APIs, and database connect.

## Architecture Summary

Evercrafted has three layers:

1. Evercrafted OS — engine and operational intelligence layer
2. Evercrafted Studio — creator-facing SaaS layer
3. Moodoor — consumer-facing emotional commerce layer

## Core Data Flow

```text
User Input
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
Design Library / BuildBloom / Render Studio / Marketplace / Moodoor
```

## Evercrafted OS Components

### Emotion Engine
Interprets memory, mood, emotional language, seasonal cues, and psychographic signals.

### Formula Engine
Selects the structural composition archetype.

### Wreath DNA Engine
Generates procedural traits that influence density, rhythm, spread, flow, focal hierarchy, and negative space.

### Placement Engine
Generates deterministic spatial coordinates.

### Placement Visualization Engine
Renders placement data into visual previews and build simulations.

### Blueprint Compiler
Normalizes every output into EC_CANON_V1.

### BuildBloom
Converts blueprint data into manufacturable assembly logic.

### Inventory Engine
Connects material availability and cost to design generation.

## Evercrafted Studio Components

Memory Weaver is the intake. Design Studio is the workspace. Inventory Weaver is the material system. Render Studio is the prompt/output system. Design Library stores blueprints and versions.

## Moodoor Components

Moodoor uses a mood quiz, match engine, and product recommendation layer powered invisibly by Evercrafted OS.

## Frontend Architecture

Recommended: Next.js, React, TypeScript, Tailwind or tokenized CSS, Canvas/SVG rendering, componentized app shell, and Zustand or equivalent state store.

Primary frontend areas: dashboard, Memory Weaver, Design Studio, Inventory Weaver, Design Library, Build Sheet view.

## Backend Architecture

Recommended: FastAPI or Node/TypeScript API, PostgreSQL, JSONB blueprint storage, server-side AI calls only, API layer for all engine functions.

Backend services: emotion service, blueprint compiler service, placement service, inventory service, build sheet service, library service.

## Security Rule

AI API keys must never live in browser/client code. All AI calls must go through backend endpoints.

## System Console Role

The uploaded System Console HTML is canonical as a reference for engine layout, module grouping, dark/gold visual doctrine, operational dashboard concept, phase architecture, and visualization-first product logic.

It should be ported into production only after MVP fundamentals are working.
