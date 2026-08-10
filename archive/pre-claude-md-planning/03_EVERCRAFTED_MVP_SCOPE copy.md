# 03_EVERCRAFTED_MVP_SCOPE

## Purpose

This file tells developers what to build first.

It is the primary scope-control document for the MVP.

## MVP Goal

Build the smallest version of Evercrafted that proves the complete engine loop:

Emotion input → blueprint → visual preview → manufacturing output → saved design.

## MVP Includes

### 1. Authentication / User Shell
- user signup/login
- workspace dashboard
- basic account structure

### 2. Memory Weaver
- text input for memory, mood, or concept
- AI emotion interpretation
- formula recommendation
- palette and design direction
- structured output

### 3. Blueprint Compiler
- produces EC_CANON_V1-compatible blueprint JSON
- stores emotion, formula, DNA, placement, materials, and metadata

### 4. Placement Engine
- deterministic placement generation
- polar coordinates
- clock positions
- zones and anchors
- no random AI placement

### 5. Placement Visualization Engine
- canvas/SVG preview
- radial guide overlays
- layered rendering
- build sequence preview if possible

### 6. Design Studio
- view/edit blueprint
- inspect placements
- adjust formula/density/basic materials
- preview visual layout

### 7. Inventory Weaver
- basic inventory entry
- material availability
- cost fields
- material selection for blueprint

### 8. BuildBloom Output
- material list
- stem counts
- build sequence
- attachment notes
- printable build sheet

### 9. Design Library
- save blueprint
- search/list saved designs
- reopen designs
- export JSON

## MVP Excludes

Do not build in MVP: full marketplace, Moodoor consumer platform, adaptive learning, psychographic clustering, full Shopify publishing, real Gmail/Calendar integrations, advanced team accounts, full subscription billing complexity, complex AI image generation pipeline, multi-user collaboration, or advanced portfolio analytics.

## MVP Success Criteria

The MVP is successful if a user can enter a memory or mood, receive a structured wreath concept, generate deterministic placement data, see a visual layout preview, save the blueprint, generate a build sheet, and export or reuse the design.

## Developer Build Priority

1. Data schema
2. Blueprint Compiler
3. Placement Engine
4. Visualization Engine
5. Memory Weaver
6. Design Studio shell
7. Design Library
8. Inventory Weaver
9. BuildBloom output
10. Polish + QA
