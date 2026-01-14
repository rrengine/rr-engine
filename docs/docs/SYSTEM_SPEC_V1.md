# SYSTEM SPEC v1 (LOCKED)

## Purpose
A deterministic rules engine that produces 3D models (starting with Sneaker v1).
AI assists only when explicitly invoked and never edits geometry-driving (instrumental) specs.

## Non-negotiables
1. Specs → Geometry → AI
2. Instrumental specs define geometry; AI cannot edit them.
3. Any change creates a NEW generation (immutable history).
4. Undo is achieved by switching active generation back.
5. Regenerate reuses unchanged data (instrumental + previous resolved non-instrumental where applicable).
6. AI is explicit, auditable, and user-approved.
7. Export must be clean: geometry file(s) separated from human-readable overlays/notes.

## Roles
- owner/edit: generate/regenerate/merge/export
- view: read-only
- factory: view geometry + tech pack, add feedback
- supplier: view BOM/materials/textures; no geometry edits
- render: access render outputs; no spec changes
- qa: validation + approval workflow

## Option Gate (when missing non-instrumental)
When instrumental valid but non-instrumental missing:
1) Continue with defaults (canonical safe defaults)
2) Cancel generation
3) Use AI suggestion as draft (AI fills missing appearance fields). User can edit after.

## AI Merge
AI can merge *non-instrumental* between two generations and propose results.
User must accept to create a new generation with source=ai_merge.
