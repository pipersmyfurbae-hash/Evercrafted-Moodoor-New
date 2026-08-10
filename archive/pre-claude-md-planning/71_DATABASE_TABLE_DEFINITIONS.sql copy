-- 71_DATABASE_TABLE_DEFINITIONS.sql
-- Evercrafted MVP database foundation
-- PostgreSQL

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email TEXT UNIQUE NOT NULL,
  name TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS blueprints (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  blueprint_id TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  version TEXT DEFAULT '1.0.0',
  formula_id TEXT,
  emotion_quadrant TEXT,
  valence NUMERIC,
  arousal NUMERIC,
  blueprint_json JSONB NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_blueprints_user_id ON blueprints(user_id);
CREATE INDEX IF NOT EXISTS idx_blueprints_formula_id ON blueprints(formula_id);
CREATE INDEX IF NOT EXISTS idx_blueprints_emotion_quadrant ON blueprints(emotion_quadrant);
CREATE INDEX IF NOT EXISTS idx_blueprints_json ON blueprints USING GIN (blueprint_json);

CREATE TABLE IF NOT EXISTS blueprint_versions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  blueprint_db_id UUID NOT NULL REFERENCES blueprints(id) ON DELETE CASCADE,
  version_num INTEGER NOT NULL,
  note TEXT,
  blueprint_json JSONB NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS placements (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  blueprint_db_id UUID NOT NULL REFERENCES blueprints(id) ON DELETE CASCADE,
  placement_id TEXT NOT NULL,
  material_id TEXT,
  role TEXT NOT NULL,
  layer TEXT NOT NULL,
  theta_deg NUMERIC NOT NULL,
  radius_norm NUMERIC NOT NULL,
  radius_in NUMERIC,
  rotation_deg NUMERIC DEFAULT 0,
  scale NUMERIC DEFAULT 1,
  z_index INTEGER DEFAULT 1,
  cluster_id TEXT,
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_placements_blueprint ON placements(blueprint_db_id);
CREATE INDEX IF NOT EXISTS idx_placements_layer ON placements(layer);

CREATE TABLE IF NOT EXISTS inventory_items (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  type TEXT NOT NULL,
  role TEXT NOT NULL,
  color TEXT,
  quantity NUMERIC DEFAULT 0,
  unit_cost NUMERIC DEFAULT 0,
  tags TEXT[] DEFAULT '{}',
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_inventory_user ON inventory_items(user_id);
CREATE INDEX IF NOT EXISTS idx_inventory_role ON inventory_items(role);
CREATE INDEX IF NOT EXISTS idx_inventory_type ON inventory_items(type);

CREATE TABLE IF NOT EXISTS build_sheets (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  blueprint_db_id UUID NOT NULL REFERENCES blueprints(id) ON DELETE CASCADE,
  build_sheet_json JSONB NOT NULL,
  estimated_minutes INTEGER,
  difficulty TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS render_jobs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  blueprint_db_id UUID REFERENCES blueprints(id) ON DELETE SET NULL,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  mode TEXT NOT NULL,
  prompt_text TEXT NOT NULL,
  status TEXT DEFAULT 'completed',
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS evaluator_scores (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  blueprint_db_id UUID NOT NULL REFERENCES blueprints(id) ON DELETE CASCADE,
  overall_score INTEGER,
  composition_balance INTEGER,
  movement_score INTEGER,
  emotional_coherence INTEGER,
  manufacturability INTEGER,
  originality INTEGER,
  warnings JSONB DEFAULT '[]'::jsonb,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS collections (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  description TEXT,
  season TEXT,
  mood TEXT,
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS collection_blueprints (
  collection_id UUID NOT NULL REFERENCES collections(id) ON DELETE CASCADE,
  blueprint_db_id UUID NOT NULL REFERENCES blueprints(id) ON DELETE CASCADE,
  sort_order INTEGER DEFAULT 0,
  PRIMARY KEY (collection_id, blueprint_db_id)
);
