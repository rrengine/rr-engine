# Next Engineering Steps (Ordered)

0) Canonical DB schema (locked)
   - users/projects/project_members
   - generations/specs/geometry_assets
   - ai_actions/merge_history/exports/comments/analytics_events

1) Geometry integration (deterministic)
   - geometry_assets table + model
   - geometry created for every generation
   - produces: mesh_uri placeholder, anchors placeholder, bounds placeholder, geometry_hash

2) Import endpoint
   - create generation source=import
   - attach imported geometry_assets

3) Export engine + factory handoff (stub)
   - profile-based export records
   - export_uri placeholder

4) Geometry versioning + invalidation
   - geometry_hash includes geom_version/params
   - stale geometry is updated (no deletes)

5) Merge-aware geometry hashing
   - parent geometry hashes included (sorted) for deterministic merge identity

6) Exports consume geometry_assets
   - export endpoint ensures geometry exists and returns geometry payload

7) Factory feedback loop
   - endpoint creates new generation source=factory_feedback
   - copies specs forward, attaches real URIs/bounds if provided

8) Caching / dedup
   - ensure_geometry_assets is no-op when hash matches
   - URIs are content-addressed by geometry_hash (storage dedup later)

9) Production gate: DB Row Level Security (RLS)
   - Apply docs/RLS.sql after schema deployment
   - API sets `app.user_id` via `set_config('app.user_id', ...)` per request
   - Keep API role checks (defense in depth)

10) Generation listing includes geometry
   - `GET /projects/{project_id}/generations` returns embedded `geometry` with `geometry_hash`, URIs, bounds
   - Backfills geometry for legacy rows if missing
