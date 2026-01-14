from __future__ import annotations

"""DB-facing geometry integration.

Implements:
 - deterministic geometry build (stub)
 - merge-aware hashing via parent geometry hashes
 - caching: no-op if geometry_hash already matches
 - invalidation: update row when hash changes

Schema note:
The canonical DB schema locks geometry_assets to ONE row per generation via UNIQUE(generation_id).
So invalidation is implemented as an UPDATE (not inserting multiple versions).
"""

from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.geometry.engine import build_geometry_stub
from app.models.geometry import GeometryAsset
from app.models.spec import SpecSnapshot
from app.models.generation import Generation


def _latest_specs(db: Session, generation_id: UUID) -> SpecSnapshot:
    snap = (
        db.query(SpecSnapshot)
        .filter(SpecSnapshot.generation_id == generation_id)
        .order_by(SpecSnapshot.created_at.desc())
        .first()
    )
    if not snap:
        raise HTTPException(status_code=404, detail="Spec snapshot not found for generation.")
    return snap


def _parent_geometry_hashes(db: Session, gen: Generation) -> list[str]:
    """Collect parent geometry hashes (for merge-aware determinism)."""
    if not gen.parent_ids:
        return []
    hashes: list[str] = []
    for pid in gen.parent_ids:
        ga = db.query(GeometryAsset).filter(GeometryAsset.generation_id == pid).one_or_none()
        if ga and ga.geometry_hash:
            hashes.append(ga.geometry_hash)
    return hashes


def ensure_geometry_assets(
    db: Session,
    *,
    generation_id: UUID,
    geom_version: str = "stub_v1",
    geom_params: dict | None = None,
) -> GeometryAsset:
    """Create or update geometry_assets for a generation.

    - Computes deterministic geometry_hash.
    - If existing record matches hash => returns it (cache hit).
    - Else updates placeholders and geometry_hash.
    """

    gen = db.query(Generation).filter(Generation.id == generation_id).one_or_none()
    if not gen:
        raise HTTPException(status_code=404, detail="Generation not found.")

    specs = _latest_specs(db, generation_id)
    parent_hashes = _parent_geometry_hashes(db, gen)

    built = build_geometry_stub(
        generation_id=str(generation_id),
        instrumental_specs=specs.instrumental_specs or {},
        geom_version=geom_version,
        geom_params=geom_params,
        parent_hashes=parent_hashes,
    )

    existing = db.query(GeometryAsset).filter(GeometryAsset.generation_id == generation_id).one_or_none()

    if existing:
        # Cache hit: do nothing if already canonical.
        if existing.geometry_hash == built["geometry_hash"]:
            return existing

        # Invalidate + update in place (schema is 1 row per generation).
        existing.mesh_uri = built["mesh_uri"]
        existing.anchors_uri = built["anchors_uri"]
        existing.bounds = built["bounds"]
        existing.geometry_hash = built["geometry_hash"]
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing

    ga = GeometryAsset(
        generation_id=generation_id,
        mesh_uri=built["mesh_uri"],
        anchors_uri=built["anchors_uri"],
        bounds=built["bounds"],
        geometry_hash=built["geometry_hash"],
    )
    db.add(ga)
    db.commit()
    db.refresh(ga)
    return ga
