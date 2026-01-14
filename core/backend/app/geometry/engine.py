"""Geometry integration (deterministic stub).

This module intentionally does NOT depend on any external CAD/mesh engine.
It provides a reproducible geometry identity (geometry_hash) and placeholder
URIs/bounds that can be replaced later by real geometry outputs.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Iterable


def _canonical_json(obj: Any) -> str:
    """Stable JSON encoding (sorted keys, no whitespace)."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def compute_geometry_hash(
    *,
    generation_id: str,
    instrumental_specs: dict,
    parent_geometry_hashes: Iterable[str] | None = None,
    geom_version: str = "stub_v1",
    geom_params: dict | None = None,
) -> str:
    """Compute a deterministic geometry hash.

    Merge-aware: parent hashes are included (sorted) so the same merge inputs
    produce the same geometry identity.
    """
    parents = sorted([h for h in (parent_geometry_hashes or []) if h])
    payload = {
        "generation_id": generation_id,
        "instrumental_specs": instrumental_specs,
        "parents": parents,
        "geom_version": geom_version,
        "geom_params": geom_params or {},
    }
    digest = hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()
    return digest


def build_geometry_stub(
    *,
    geometry_hash: str,
    uri_scheme: str = "geom://",
) -> dict:
    """Return placeholders keyed by geometry_hash."""
    # Storage URIs are placeholders for now; later these can become s3://... etc.
    mesh_uri = f"{uri_scheme}mesh/{geometry_hash}.glb"
    anchors_uri = f"{uri_scheme}anchors/{geometry_hash}.json"
    bounds = {"min": [0, 0, 0], "max": [1, 1, 1], "units": "normalized"}
    return {
        "mesh_uri": mesh_uri,
        "anchors_uri": anchors_uri,
        "bounds": bounds,
        "geometry_hash": geometry_hash,
    }
