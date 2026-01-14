import hashlib
import json

def build_geometry(instrumental_specs: dict) -> dict:
    payload = json.dumps(instrumental_specs, sort_keys=True)
    geometry_hash = hashlib.sha256(payload.encode()).hexdigest()
    # In production, these would be real storage URIs
    return {
        "mesh_uri": f"meshes/{geometry_hash}.glb",
        "anchors_uri": f"anchors/{geometry_hash}.json",
        "bounds": {"min": [0,0,0], "max": [0,0,0]},
        "geometry_hash": geometry_hash,
    }
