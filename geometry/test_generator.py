"""
Test script for shoe geometry generation.
Run this to verify the geometry engine produces valid output.
"""

import logging
import sys
from pathlib import Path

from shoe_generator import InstrumentalSpecs, generate_and_export, generate_shoe_mesh

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def test_basic_generation():
    """Test basic shoe generation with default specs."""
    specs = InstrumentalSpecs(
        shoe_length_mm=280.0,
        shoe_width_mm=105.0,
        sole_thickness_mm=30.0,
        arch_height_mm=15.0,
        toe_spring_mm=12.0,
        collar_height_mm=55.0,
    )

    logger.info("Testing basic generation...")
    result = generate_shoe_mesh(specs)

    assert result.vertex_count > 0, "Mesh should have vertices"
    assert result.face_count > 0, "Mesh should have faces"
    # Shoe mesh is not watertight (has opening at collar) - check for valid faces instead
    assert not result.mesh.is_empty, "Mesh should not be empty"
    assert result.mesh.faces.shape[1] == 3, "Faces should be triangles"
    assert len(result.geometry_hash) == 16, "Hash should be 16 characters"

    logger.info(f"  Vertices: {result.vertex_count}")
    logger.info(f"  Faces: {result.face_count}")
    logger.info(f"  Bounds: {result.bounds_min} to {result.bounds_max}")
    logger.info(f"  Hash: {result.geometry_hash}")
    logger.info("  PASSED")

    return result


def test_export_pipeline():
    """Test full export pipeline."""
    specs = InstrumentalSpecs(
        shoe_length_mm=290.0,
        shoe_width_mm=110.0,
        sole_thickness_mm=35.0,
        arch_height_mm=20.0,
        toe_spring_mm=15.0,
        collar_height_mm=60.0,
    )

    output_dir = Path(__file__).parent / "test_output"

    logger.info("Testing export pipeline...")
    result = generate_and_export(specs, output_dir)

    glb_path = Path(result["mesh_uri"])
    anchors_path = Path(result["anchors_uri"])

    assert glb_path.exists(), f"GLB file should exist at {glb_path}"
    assert anchors_path.exists(), f"Anchors file should exist at {anchors_path}"
    assert glb_path.stat().st_size > 0, "GLB file should not be empty"

    logger.info(f"  GLB: {glb_path} ({glb_path.stat().st_size} bytes)")
    logger.info(f"  Anchors: {anchors_path}")
    logger.info(f"  Hash: {result['geometry_hash']}")
    logger.info("  PASSED")

    return result


def test_deterministic_hash():
    """Test that same specs produce same hash."""
    specs1 = InstrumentalSpecs(
        shoe_length_mm=280.0,
        shoe_width_mm=105.0,
        sole_thickness_mm=30.0,
        arch_height_mm=15.0,
        toe_spring_mm=12.0,
        collar_height_mm=55.0,
    )

    specs2 = InstrumentalSpecs(
        shoe_length_mm=280.0,
        shoe_width_mm=105.0,
        sole_thickness_mm=30.0,
        arch_height_mm=15.0,
        toe_spring_mm=12.0,
        collar_height_mm=55.0,
    )

    logger.info("Testing deterministic hashing...")
    assert specs1.geometry_hash() == specs2.geometry_hash(), "Same specs should produce same hash"
    logger.info(f"  Hash: {specs1.geometry_hash()}")
    logger.info("  PASSED")


def test_validation():
    """Test that invalid specs are rejected."""
    logger.info("Testing validation...")

    try:
        specs = InstrumentalSpecs(
            shoe_length_mm=500.0,  # Too long
            shoe_width_mm=105.0,
            sole_thickness_mm=30.0,
            arch_height_mm=15.0,
            toe_spring_mm=12.0,
            collar_height_mm=55.0,
        )
        specs.validate()
        logger.error("  FAILED: Should have rejected invalid specs")
        return False
    except ValueError as e:
        logger.info(f"  Correctly rejected: {e}")
        logger.info("  PASSED")
        return True


def test_size_variants():
    """Test generation across different sizes."""
    logger.info("Testing size variants...")

    sizes = [
        ("Small", 260, 95),
        ("Medium", 280, 105),
        ("Large", 310, 120),
    ]

    output_dir = Path(__file__).parent / "test_output" / "sizes"

    for name, length, width in sizes:
        specs = InstrumentalSpecs(
            shoe_length_mm=float(length),
            shoe_width_mm=float(width),
            sole_thickness_mm=30.0,
            arch_height_mm=15.0,
            toe_spring_mm=12.0,
            collar_height_mm=55.0,
        )

        result = generate_and_export(specs, output_dir)
        logger.info(f"  {name}: {result['vertex_count']} verts, hash={result['geometry_hash']}")

    logger.info("  PASSED")


def main():
    """Run all tests."""
    logger.info("=" * 60)
    logger.info("SHOE GEOMETRY ENGINE TESTS")
    logger.info("=" * 60)

    try:
        test_basic_generation()
        test_export_pipeline()
        test_deterministic_hash()
        test_validation()
        test_size_variants()

        logger.info("=" * 60)
        logger.info("ALL TESTS PASSED")
        logger.info("=" * 60)
        return 0
    except Exception as e:
        logger.error(f"TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
