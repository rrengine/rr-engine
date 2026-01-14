"""
Production-grade parametric shoe mesh generator.

Generates real 3D shoe geometry from instrumental specifications.
Uses Trimesh for mesh operations and exports to GLB format.
"""

import hashlib
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

import numpy as np
import trimesh
from scipy.spatial import Delaunay

logger = logging.getLogger(__name__)


@dataclass
class InstrumentalSpecs:
    """Geometry-driving specifications for shoe generation."""
    shoe_length_mm: float
    shoe_width_mm: float
    sole_thickness_mm: float
    arch_height_mm: float
    toe_spring_mm: float
    collar_height_mm: float

    def validate(self) -> None:
        """Validate specs are within manufacturing constraints."""
        constraints = {
            "shoe_length_mm": (250, 330),
            "shoe_width_mm": (90, 130),
            "sole_thickness_mm": (20, 45),
            "arch_height_mm": (5, 35),
            "toe_spring_mm": (5, 25),
            "collar_height_mm": (30, 90),
        }
        for field, (min_val, max_val) in constraints.items():
            value = getattr(self, field)
            if not min_val <= value <= max_val:
                raise ValueError(
                    f"{field}={value} outside valid range [{min_val}, {max_val}]"
                )

    def to_dict(self) -> dict:
        return {
            "shoe_length_mm": self.shoe_length_mm,
            "shoe_width_mm": self.shoe_width_mm,
            "sole_thickness_mm": self.sole_thickness_mm,
            "arch_height_mm": self.arch_height_mm,
            "toe_spring_mm": self.toe_spring_mm,
            "collar_height_mm": self.collar_height_mm,
        }

    def geometry_hash(self) -> str:
        """Compute deterministic hash for these specs."""
        canonical = json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode()).hexdigest()[:16]


@dataclass
class AnchorPoints:
    """Attachment points for accessories and branding."""
    toe_box_center: Tuple[float, float, float]
    heel_center: Tuple[float, float, float]
    lateral_midfoot: Tuple[float, float, float]
    medial_midfoot: Tuple[float, float, float]
    tongue_top: Tuple[float, float, float]
    collar_back: Tuple[float, float, float]


@dataclass
class GeometryResult:
    """Complete geometry output with mesh, anchors, and metadata."""
    mesh: trimesh.Trimesh
    anchors: AnchorPoints
    bounds_min: Tuple[float, float, float]
    bounds_max: Tuple[float, float, float]
    geometry_hash: str
    vertex_count: int
    face_count: int


def _generate_sole_profile(specs: InstrumentalSpecs, num_points: int = 50) -> np.ndarray:
    """
    Generate 2D sole outline profile.

    Returns array of (x, y) points defining the sole perimeter.
    The sole is symmetric and follows a natural foot shape.
    """
    length = specs.shoe_length_mm
    width = specs.shoe_width_mm

    t = np.linspace(0, 2 * np.pi, num_points, endpoint=False)

    # Parametric foot-shaped curve
    # Wider at ball of foot, narrower at heel and toe
    x = length / 2 * np.cos(t)

    # Width modulation: narrower at toe (front) and heel (back)
    width_factor = np.where(
        np.cos(t) > 0,
        # Front half: toe taper
        0.7 + 0.3 * np.cos(t * 2),
        # Back half: heel taper
        0.8 + 0.2 * np.cos(t * 2)
    )
    y = width / 2 * np.sin(t) * width_factor

    # Shift so heel is at origin, toe at length
    x = x + length / 2

    return np.column_stack([x, y])


def _generate_sole_mesh(specs: InstrumentalSpecs) -> trimesh.Trimesh:
    """
    Generate the sole/midsole as a 3D mesh.

    Creates a extruded sole with:
    - Flat bottom for ground contact
    - Arch support curve on top
    - Toe spring (upward curve at front)
    """
    profile = _generate_sole_profile(specs)
    num_profile_points = len(profile)

    thickness = specs.sole_thickness_mm
    arch_height = specs.arch_height_mm
    toe_spring = specs.toe_spring_mm
    length = specs.shoe_length_mm

    # Create vertices for top and bottom of sole
    vertices = []

    # Bottom vertices (flat, z=0)
    for x, y in profile:
        vertices.append([x, y, 0.0])

    # Top vertices with arch and toe spring
    for x, y in profile:
        # Normalized position along length (0 = heel, 1 = toe)
        t = x / length

        # Arch curve: parabolic, peaks at midfoot
        arch_offset = arch_height * 4 * t * (1 - t)

        # Toe spring: exponential rise at front
        toe_offset = toe_spring * max(0, (t - 0.8) / 0.2) ** 2 if t > 0.8 else 0

        z = thickness + arch_offset + toe_offset
        vertices.append([x, y, z])

    vertices = np.array(vertices)

    # Create faces using triangulation
    faces = []

    # Bottom face (triangulate the profile)
    bottom_points = profile
    tri = Delaunay(bottom_points)
    for simplex in tri.simplices:
        # Reverse winding for outward normal (down)
        faces.append([simplex[0], simplex[2], simplex[1]])

    # Top face
    for simplex in tri.simplices:
        offset = num_profile_points
        faces.append([simplex[0] + offset, simplex[1] + offset, simplex[2] + offset])

    # Side faces connecting top and bottom
    for i in range(num_profile_points):
        next_i = (i + 1) % num_profile_points
        bottom_curr = i
        bottom_next = next_i
        top_curr = i + num_profile_points
        top_next = next_i + num_profile_points

        # Two triangles per quad
        faces.append([bottom_curr, bottom_next, top_next])
        faces.append([bottom_curr, top_next, top_curr])

    faces = np.array(faces)

    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
    mesh.fix_normals()

    return mesh


def _generate_upper_mesh(specs: InstrumentalSpecs, sole_mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    """
    Generate the shoe upper (top part covering the foot).

    Creates a shell that:
    - Sits on top of the sole
    - Has a collar opening at the ankle
    - Follows foot contour
    """
    length = specs.shoe_length_mm
    width = specs.shoe_width_mm
    collar_height = specs.collar_height_mm
    sole_thickness = specs.sole_thickness_mm
    arch_height = specs.arch_height_mm

    # Get sole top boundary for attachment
    sole_bounds = sole_mesh.bounds
    sole_top_z = sole_bounds[1, 2]

    vertices = []
    faces = []

    # Generate upper as a series of cross-sectional rings
    num_sections = 30
    points_per_section = 24

    for i in range(num_sections):
        t = i / (num_sections - 1)  # 0 = heel, 1 = toe
        x = t * length

        # Section width varies along length
        if t < 0.3:
            # Heel section: narrower
            section_width = width * (0.7 + t)
        elif t < 0.7:
            # Midfoot: full width
            section_width = width
        else:
            # Toe: tapers
            section_width = width * (1 - 0.5 * (t - 0.7) / 0.3)

        # Height varies: higher at ankle, lower at toe
        if t < 0.2:
            # Collar/ankle area
            section_height = collar_height
        elif t < 0.4:
            # Transition
            section_height = collar_height * (1 - (t - 0.2) / 0.2 * 0.5)
        else:
            # Vamp/toe area
            section_height = collar_height * 0.5 * (1 - (t - 0.4) / 0.6 * 0.3)

        # Sole top height at this x position
        sole_z = sole_thickness + arch_height * 4 * t * (1 - t)

        # Generate points around this section (semi-circle, open at bottom)
        for j in range(points_per_section):
            angle = np.pi * j / (points_per_section - 1)  # 0 to pi (semicircle)

            y = section_width / 2 * np.cos(angle)
            z = sole_z + section_height * np.sin(angle)

            vertices.append([x, y, z])

    vertices = np.array(vertices)

    # Create faces between adjacent sections
    for i in range(num_sections - 1):
        for j in range(points_per_section - 1):
            curr = i * points_per_section + j
            next_j = curr + 1
            curr_next_section = (i + 1) * points_per_section + j
            next_j_next_section = curr_next_section + 1

            # Two triangles per quad
            faces.append([curr, curr_next_section, next_j])
            faces.append([next_j, curr_next_section, next_j_next_section])

    # Cap the toe
    toe_center_idx = len(vertices)
    toe_section_start = (num_sections - 1) * points_per_section
    toe_center = vertices[toe_section_start:toe_section_start + points_per_section].mean(axis=0)
    vertices = np.vstack([vertices, toe_center])

    for j in range(points_per_section - 1):
        faces.append([
            toe_section_start + j,
            toe_section_start + j + 1,
            toe_center_idx
        ])

    # Cap the heel (back)
    heel_center_idx = len(vertices)
    heel_center = vertices[:points_per_section].mean(axis=0)
    vertices = np.vstack([vertices, heel_center])

    for j in range(points_per_section - 1):
        faces.append([
            j + 1,
            j,
            heel_center_idx
        ])

    faces = np.array(faces)

    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
    mesh.fix_normals()

    return mesh


def _compute_anchor_points(specs: InstrumentalSpecs, combined_mesh: trimesh.Trimesh) -> AnchorPoints:
    """Compute anchor points for accessories and branding placement."""
    length = specs.shoe_length_mm
    width = specs.shoe_width_mm
    sole_thickness = specs.sole_thickness_mm
    collar_height = specs.collar_height_mm

    bounds = combined_mesh.bounds

    return AnchorPoints(
        toe_box_center=(length * 0.9, 0.0, sole_thickness + collar_height * 0.3),
        heel_center=(length * 0.05, 0.0, sole_thickness + collar_height * 0.5),
        lateral_midfoot=(length * 0.5, width * 0.45, sole_thickness + collar_height * 0.4),
        medial_midfoot=(length * 0.5, -width * 0.45, sole_thickness + collar_height * 0.4),
        tongue_top=(length * 0.3, 0.0, sole_thickness + collar_height * 0.9),
        collar_back=(length * 0.1, 0.0, sole_thickness + collar_height),
    )


def generate_shoe_mesh(specs: InstrumentalSpecs) -> GeometryResult:
    """
    Generate complete shoe geometry from instrumental specifications.

    Args:
        specs: Validated instrumental specifications

    Returns:
        GeometryResult containing mesh, anchors, bounds, and metadata

    Raises:
        ValueError: If specs are outside valid manufacturing ranges
    """
    specs.validate()

    logger.info(f"Generating shoe mesh for specs hash: {specs.geometry_hash()}")

    # Generate component meshes
    sole_mesh = _generate_sole_mesh(specs)
    upper_mesh = _generate_upper_mesh(specs, sole_mesh)

    # Combine into single mesh
    combined_mesh = trimesh.util.concatenate([sole_mesh, upper_mesh])
    combined_mesh.fix_normals()

    # Merge duplicate vertices for cleaner mesh
    combined_mesh.merge_vertices()

    # Compute anchor points
    anchors = _compute_anchor_points(specs, combined_mesh)

    # Get bounds
    bounds_min = tuple(combined_mesh.bounds[0].tolist())
    bounds_max = tuple(combined_mesh.bounds[1].tolist())

    logger.info(
        f"Generated mesh: {len(combined_mesh.vertices)} vertices, "
        f"{len(combined_mesh.faces)} faces"
    )

    return GeometryResult(
        mesh=combined_mesh,
        anchors=anchors,
        bounds_min=bounds_min,
        bounds_max=bounds_max,
        geometry_hash=specs.geometry_hash(),
        vertex_count=len(combined_mesh.vertices),
        face_count=len(combined_mesh.faces),
    )


def export_to_glb(result: GeometryResult, output_dir: Path) -> Path:
    """
    Export geometry to GLB format.

    Args:
        result: GeometryResult from generate_shoe_mesh
        output_dir: Directory to write files

    Returns:
        Path to the exported GLB file
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    glb_path = output_dir / f"{result.geometry_hash}.glb"

    # Export mesh to GLB
    result.mesh.export(str(glb_path), file_type="glb")

    logger.info(f"Exported GLB to {glb_path}")

    return glb_path


def export_anchors(result: GeometryResult, output_dir: Path) -> Path:
    """
    Export anchor points to JSON.

    Args:
        result: GeometryResult from generate_shoe_mesh
        output_dir: Directory to write files

    Returns:
        Path to the exported JSON file
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    anchors_path = output_dir / f"{result.geometry_hash}_anchors.json"

    anchors_dict = {
        "toe_box_center": list(result.anchors.toe_box_center),
        "heel_center": list(result.anchors.heel_center),
        "lateral_midfoot": list(result.anchors.lateral_midfoot),
        "medial_midfoot": list(result.anchors.medial_midfoot),
        "tongue_top": list(result.anchors.tongue_top),
        "collar_back": list(result.anchors.collar_back),
    }

    with open(anchors_path, "w") as f:
        json.dump(anchors_dict, f, indent=2)

    logger.info(f"Exported anchors to {anchors_path}")

    return anchors_path


def generate_and_export(
    specs: InstrumentalSpecs,
    output_dir: Path
) -> dict:
    """
    Full pipeline: generate mesh and export all assets.

    Args:
        specs: Instrumental specifications
        output_dir: Directory for output files

    Returns:
        Dictionary with mesh_uri, anchors_uri, bounds, and geometry_hash
    """
    result = generate_shoe_mesh(specs)

    glb_path = export_to_glb(result, output_dir)
    anchors_path = export_anchors(result, output_dir)

    return {
        "mesh_uri": str(glb_path),
        "anchors_uri": str(anchors_path),
        "bounds": {
            "min": list(result.bounds_min),
            "max": list(result.bounds_max),
        },
        "geometry_hash": result.geometry_hash,
        "vertex_count": result.vertex_count,
        "face_count": result.face_count,
    }
