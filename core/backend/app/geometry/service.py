"""DB-facing geometry helpers.

This is the single integration point used by API routes:

- ensure a generation has a geometry_assets row
- compute deterministic geometry_hash (merge-aware)
- update existing rows (schema enforces 1 row per generation)

Later: swap in a real geometry engine and only change this layer.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.geometry.engine import compute_geometry_hash, build_geometry_stub
from app.models.generation import Generation
from app.models.spec import SpecSnapshot
from app.models.geometry import GeometryAsset


def _latest_specs(db: Session, generation_id: UUID) -> SpecSnapshot:
    snap = (
        db.query(SpecSnapshot)
        .filter(SpecSnapshot.generation_id == generation_id)
        .order_by(SpecSnapshot.created_at.desc())
        .first()
    )
    if not snap:
        raise ValueError("Spec snapshot not found for generation.")
    return snap


def ensure_geometry_assets(
    db: Session,
    generation_id: UUID,
    *,
    geom_version: str = "stub_v1",
    geom_params: dict | None = None,
    uri_scheme: str = "geom://",
) -> GeometryAsset:
    """Ensure geometry_assets exists and is up-to-date for generation.

    Caching/dedup behavior:
    - If the computed geometry_hash matches existing row => no-op
    - Otherwise update row with new hash + placeholder URIs/bounds
    """
    gen = db.query(Generation).filter(Generation.id == generation_id).one_or_none()
    if not gen:
        raise ValueError("Generation not found.")

    # Ensure parent geometry exists, then collect hashes (merge-aware).
    parent_hashes: list[str] = []
    if gen.parent_ids:
        for pid in gen.parent_ids:
            parent_asset = db.query(GeometryAsset).filter(GeometryAsset.generation_id == pid).one_or_none()
            if not parent_asset:
                parent_asset = ensure_geometry_assets(
                    db,
                    pid,
                    geom_version=geom_version,
                    geom_params=geom_params,
                    uri_scheme=uri_scheme,
                )
            parent_hashes.append(parent_asset.geometry_hash)

    specs = _latest_specs(db, generation_id)

    computed_hash = compute_geometry_hash(
        generation_id=str(generation_id),
        instrumental_specs=specs.instrumental_specs or {},
        parent_geometry_hashes=parent_hashes,
        geom_version=geom_version,
        geom_params=geom_params,
    )

    existing = db.query(GeometryAsset).filter(GeometryAsset.generation_id == generation_id).one_or_none()
    if existing and existing.geometry_hash == computed_hash:
        return existing

    stub = build_geometry_stub(geometry_hash=computed_hash, uri_scheme=uri_scheme)

    if not existing:
        existing = GeometryAsset(
            generation_id=generation_id,
            mesh_uri=stub["mesh_uri"],
            anchors_uri=stub["anchors_uri"],
            bounds=stub["bounds"],
            geometry_hash=stub["geometry_hash"],
        )
        db.add(existing)
    else:
        existing.mesh_uri = stub["mesh_uri"]
        existing.anchors_uri = stub["anchors_uri"]
        existing.bounds = stub["bounds"]
        existing.geometry_hash = stub["geometry_hash"]

    db.commit()
    db.refresh(existing)
    return existing
