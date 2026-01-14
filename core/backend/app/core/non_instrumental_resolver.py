from typing import Dict, Any, List, Tuple
from copy import deepcopy
from app.core.spec_requirements import NON_INSTRUMENTAL_CANONICAL

def _ensure_dict(root: Dict[str, Any], key: str) -> Dict[str, Any]:
    if key not in root or not isinstance(root[key], dict):
        root[key] = {}
    return root[key]

def apply_canonical_defaults_for_missing(non_instrumental_specs: Dict[str, Any] | None) -> Tuple[Dict[str, Any], List[str]]:
    updated = deepcopy(non_instrumental_specs or {})
    applied: List[str] = []

    canonical_defaults = {
        "materials": {"upper": "smooth_leather", "lining": "mesh_lining", "outsole": "rubber_outsole"},
        "colors": {"primary_hex": "#000000", "secondary_hex": "#FFFFFF"},
        "branding": {"monogram_placement": "heel+toebox", "embroidery_thread": "white_thread"},
        "textures": {"upper_texture": "none"},
    }

    for section, fields in NON_INSTRUMENTAL_CANONICAL.items():
        section_dict = _ensure_dict(updated, section)
        for field in fields.keys():
            if field not in section_dict:
                section_dict[field] = canonical_defaults[section][field]
                applied.append(f"{section}.{field}")
    return updated, applied

def create_ai_draft_non_instrumental(non_instrumental_specs: Dict[str, Any] | None) -> Tuple[Dict[str, Any], List[str]]:
    base = deepcopy(non_instrumental_specs or {})
    applied: List[str] = []

    draft = {
        "materials": {"upper": "croc_print_leather", "lining": "premium_mesh", "outsole": "rubber_outsole"},
        "colors": {"primary_hex": "#0A0A0A", "secondary_hex": "#F2F2F2"},
        "branding": {"monogram_placement": "heel+toebox", "embroidery_thread": "white_thread"},
        "textures": {"upper_texture": "croc_print_tile_v1"},
    }

    for section, section_fields in draft.items():
        section_dict = _ensure_dict(base, section)
        for field, value in section_fields.items():
            if field not in section_dict:
                section_dict[field] = value
                applied.append(f"{section}.{field}")
    return base, applied
