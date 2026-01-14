INSTRUMENTAL_REQUIRED = {
    "overall_dimensions": {
        "shoe_length_mm": {"type": "number", "min": 250, "max": 330},
        "shoe_width_mm": {"type": "number", "min": 90, "max": 130},
        "sole_thickness_mm": {"type": "number", "min": 20, "max": 45},
    },
    "last_profile": {
        "arch_height_mm": {"type": "number", "min": 5, "max": 35},
        "toe_spring_mm": {"type": "number", "min": 5, "max": 25},
    },
    "collar_geometry": {
        "collar_height_mm": {"type": "number", "min": 30, "max": 90},
    },
}

NON_INSTRUMENTAL_CANONICAL = {
    "materials": {
        "upper": {"type": "string"},
        "lining": {"type": "string"},
        "outsole": {"type": "string"},
    },
    "colors": {
        "primary_hex": {"type": "string"},
        "secondary_hex": {"type": "string"},
    },
    "branding": {
        "monogram_placement": {"type": "string"},
        "embroidery_thread": {"type": "string"},
    },
    "textures": {
        "upper_texture": {"type": "string"},
    },
}
