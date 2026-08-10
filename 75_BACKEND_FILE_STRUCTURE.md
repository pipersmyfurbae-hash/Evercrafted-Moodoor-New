# 75_BACKEND_FILE_STRUCTURE

## Purpose

Defines the production backend file structure for Evercrafted Studio MVP.

---

## FastAPI Recommended Structure

```text
/backend
  /app
    main.py

    /api
      /routes
        auth.py
        health.py
        emotion.py
        placement.py
        blueprints.py
        inventory.py
        build_sheets.py
        render_prompts.py

    /core
      config.py
      security.py
      errors.py

    /db
      session.py
      migrations/

    /models
      user.py
      blueprint.py
      inventory_item.py
      build_sheet.py
      render_job.py

    /schemas
      user_schema.py
      blueprint_schema.py
      emotion_schema.py
      placement_schema.py
      inventory_schema.py
      build_sheet_schema.py

    /services
      auth_service.py
      emotion_service.py
      formula_service.py
      dna_service.py
      placement_service.py
      blueprint_compiler.py
      inventory_service.py
      buildbloom_service.py
      render_prompt_service.py

    /validators
      blueprint_validator.py
      placement_validator.py

    /utils
      polar_utils.py
      clock_utils.py
      id_utils.py
```

---

## Service Responsibilities

### emotion_service
Server-side AI emotional interpretation.

### formula_service
Deterministic formula selection.

### dna_service
Deterministic procedural trait generation.

### placement_service
Deterministic polar placement.

### blueprint_compiler
Creates EC_CANON_V1.

### buildbloom_service
Creates manufacturing build sheet.

---

## Backend Rule

All AI calls live server-side only.
