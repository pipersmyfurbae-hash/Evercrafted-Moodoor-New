-- Evercrafted Studio — Foundational Schema
-- Schema version: EC_CANON_V1
-- Database: PostgreSQL
-- Ticket: 1.4 — Database Foundation
--
-- This file is the canonical table reference.
-- It is not a live migration. No migration runner is wired yet.


-- ─────────────────────────────────────────────
-- USERS
-- Minimal user record. No auth fields in scope.
-- ─────────────────────────────────────────────

CREATE TABLE users (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    email       TEXT        NOT NULL UNIQUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- ─────────────────────────────────────────────
-- BLUEPRINTS
-- Top-level design document. Follows EC_CANON_V1.
-- emotion column stores the full EmotionInterpretation
-- object as JSONB (tone, intensity, keywords, summary).
-- ─────────────────────────────────────────────

CREATE TABLE blueprints (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    schema_version  TEXT        NOT NULL DEFAULT 'EC_CANON_V1',
    name            TEXT        NOT NULL,
    status          TEXT        NOT NULL DEFAULT 'draft'
                                CHECK (status IN ('draft', 'saved', 'archived')),
    emotion         JSONB       NOT NULL,
    user_id         UUID        NOT NULL REFERENCES users(id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- ─────────────────────────────────────────────
-- PLACEMENTS
-- One row per placed element within a blueprint.
-- Fields match PlacementEntry in @evercrafted/shared.
-- ─────────────────────────────────────────────

CREATE TABLE placements (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    blueprint_id    UUID        NOT NULL REFERENCES blueprints(id),
    role            TEXT        NOT NULL
                                CHECK (role IN ('focal', 'secondary', 'filler', 'accent', 'greenery')),
    angle           NUMERIC     NOT NULL CHECK (angle >= 0 AND angle <= 360),
    radius          NUMERIC     NOT NULL CHECK (radius >= 0.0 AND radius <= 1.0),
    layer           INTEGER     NOT NULL,
    z_index         INTEGER     NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
