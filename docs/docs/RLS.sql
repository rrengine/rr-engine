-- RR SYSTEM v1 — Row Level Security (RLS)
-- Apply after schema.sql is deployed.
--
-- Assumptions:
--   - Postgres
--   - The app sets:  set_config('app.user_id', '<uuid>', true)
--
-- Notes:
--   - These policies harden access at the database layer.
--   - The API should still enforce roles (defense in depth).

BEGIN;

-- 1) Helper schema + functions
CREATE SCHEMA IF NOT EXISTS rr;

CREATE OR REPLACE FUNCTION rr.current_user_id()
RETURNS uuid
LANGUAGE sql
STABLE
AS $$
  SELECT NULLIF(current_setting('app.user_id', true), '')::uuid;
$$;

CREATE OR REPLACE FUNCTION rr.is_project_member(p_project_id uuid)
RETURNS boolean
LANGUAGE sql
STABLE
AS $$
  SELECT EXISTS(
    SELECT 1
    FROM project_members pm
    WHERE pm.project_id = p_project_id
      AND pm.user_id = rr.current_user_id()
      AND (pm.expires_at IS NULL OR pm.expires_at > now())
  );
$$;

CREATE OR REPLACE FUNCTION rr.has_project_role(p_project_id uuid, p_roles text[])
RETURNS boolean
LANGUAGE sql
STABLE
AS $$
  SELECT EXISTS(
    SELECT 1
    FROM project_members pm
    WHERE pm.project_id = p_project_id
      AND pm.user_id = rr.current_user_id()
      AND pm.role = ANY(p_roles)
      AND (pm.expires_at IS NULL OR pm.expires_at > now())
  );
$$;

-- 2) Enable RLS
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE generations ENABLE ROW LEVEL SECURITY;
ALTER TABLE specs ENABLE ROW LEVEL SECURITY;
ALTER TABLE geometry_assets ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_actions ENABLE ROW LEVEL SECURITY;
ALTER TABLE merge_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE generation_labels ENABLE ROW LEVEL SECURITY;
ALTER TABLE generation_favorites ENABLE ROW LEVEL SECURITY;
ALTER TABLE exports ENABLE ROW LEVEL SECURITY;
ALTER TABLE comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE analytics_events ENABLE ROW LEVEL SECURITY;

-- Optional: lock down table access to force RLS (recommended in production).
-- ALTER TABLE projects FORCE ROW LEVEL SECURITY;
-- (repeat for other tables if your DB user is table owner or has BYPASSRLS)

-- 3) Policies
-- projects: members can read; owners can write
DROP POLICY IF EXISTS projects_select ON projects;
CREATE POLICY projects_select ON projects
  FOR SELECT USING (rr.is_project_member(id));

DROP POLICY IF EXISTS projects_insert ON projects;
CREATE POLICY projects_insert ON projects
  FOR INSERT WITH CHECK (owner_id = rr.current_user_id());

DROP POLICY IF EXISTS projects_update ON projects;
CREATE POLICY projects_update ON projects
  FOR UPDATE USING (owner_id = rr.current_user_id())
  WITH CHECK (owner_id = rr.current_user_id());

-- project_members: members can read; owners can manage
DROP POLICY IF EXISTS project_members_select ON project_members;
CREATE POLICY project_members_select ON project_members
  FOR SELECT USING (rr.is_project_member(project_id));

DROP POLICY IF EXISTS project_members_manage ON project_members;
CREATE POLICY project_members_manage ON project_members
  FOR ALL USING (rr.has_project_role(project_id, ARRAY['owner']))
  WITH CHECK (rr.has_project_role(project_id, ARRAY['owner']));

-- generations: members can read; edit/owner can write
DROP POLICY IF EXISTS generations_select ON generations;
CREATE POLICY generations_select ON generations
  FOR SELECT USING (rr.is_project_member(project_id));

DROP POLICY IF EXISTS generations_insert ON generations;
CREATE POLICY generations_insert ON generations
  FOR INSERT WITH CHECK (
    rr.has_project_role(project_id, ARRAY['owner','edit'])
    AND created_by = rr.current_user_id()
  );

DROP POLICY IF EXISTS generations_update ON generations;
CREATE POLICY generations_update ON generations
  FOR UPDATE USING (rr.has_project_role(project_id, ARRAY['owner','edit']))
  WITH CHECK (rr.has_project_role(project_id, ARRAY['owner','edit']));

-- specs: accessible via generation->project membership
DROP POLICY IF EXISTS specs_select ON specs;
CREATE POLICY specs_select ON specs
  FOR SELECT USING (
    EXISTS(
      SELECT 1
      FROM generations g
      WHERE g.id = specs.generation_id
        AND rr.is_project_member(g.project_id)
    )
  );

DROP POLICY IF EXISTS specs_insert ON specs;
CREATE POLICY specs_insert ON specs
  FOR INSERT WITH CHECK (
    EXISTS(
      SELECT 1
      FROM generations g
      WHERE g.id = specs.generation_id
        AND rr.has_project_role(g.project_id, ARRAY['owner','edit'])
    )
  );

-- geometry_assets: accessible via generation->project membership
DROP POLICY IF EXISTS geometry_assets_select ON geometry_assets;
CREATE POLICY geometry_assets_select ON geometry_assets
  FOR SELECT USING (
    EXISTS(
      SELECT 1
      FROM generations g
      WHERE g.id = geometry_assets.generation_id
        AND rr.is_project_member(g.project_id)
    )
  );

DROP POLICY IF EXISTS geometry_assets_upsert ON geometry_assets;
CREATE POLICY geometry_assets_upsert ON geometry_assets
  FOR ALL USING (
    EXISTS(
      SELECT 1
      FROM generations g
      WHERE g.id = geometry_assets.generation_id
        AND rr.has_project_role(g.project_id, ARRAY['owner','edit','factory','supplier','render','qa'])
    )
  )
  WITH CHECK (
    EXISTS(
      SELECT 1
      FROM generations g
      WHERE g.id = geometry_assets.generation_id
        AND rr.has_project_role(g.project_id, ARRAY['owner','edit','factory','supplier','render','qa'])
    )
  );

-- Comments/exports/analytics: members can read; certain roles can write
-- (Keep policies simple; tighten later if you want per-role granularity.)

DROP POLICY IF EXISTS comments_select ON comments;
CREATE POLICY comments_select ON comments
  FOR SELECT USING (
    EXISTS(
      SELECT 1
      FROM generations g
      WHERE g.id = comments.generation_id
        AND rr.is_project_member(g.project_id)
    )
  );

DROP POLICY IF EXISTS comments_insert ON comments;
CREATE POLICY comments_insert ON comments
  FOR INSERT WITH CHECK (
    author_id = rr.current_user_id()
    AND EXISTS(
      SELECT 1
      FROM generations g
      WHERE g.id = comments.generation_id
        AND rr.has_project_role(g.project_id, ARRAY['owner','edit','factory','supplier','render','qa','view'])
    )
  );

DROP POLICY IF EXISTS exports_select ON exports;
CREATE POLICY exports_select ON exports
  FOR SELECT USING (
    EXISTS(
      SELECT 1
      FROM generations g
      WHERE g.id = exports.generation_id
        AND rr.is_project_member(g.project_id)
    )
  );

DROP POLICY IF EXISTS exports_insert ON exports;
CREATE POLICY exports_insert ON exports
  FOR INSERT WITH CHECK (
    EXISTS(
      SELECT 1
      FROM generations g
      WHERE g.id = exports.generation_id
        AND rr.has_project_role(g.project_id, ARRAY['owner','edit','factory','supplier','render','qa'])
    )
  );

DROP POLICY IF EXISTS analytics_select ON analytics_events;
CREATE POLICY analytics_select ON analytics_events
  FOR SELECT USING (rr.is_project_member(project_id));

DROP POLICY IF EXISTS analytics_insert ON analytics_events;
CREATE POLICY analytics_insert ON analytics_events
  FOR INSERT WITH CHECK (rr.is_project_member(project_id));

COMMIT;
