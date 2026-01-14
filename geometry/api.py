"""
Geometry API Server

FastAPI server for the geometry generation engine.
Serves generated GLB files and provides generation endpoints.
"""

import logging
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from shoe_generator import InstrumentalSpecs, generate_and_export

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="RR Engine Geometry API",
    description="Production-grade 3D shoe geometry generation",
    version="1.0.0",
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Output directory for generated meshes
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# Mount static files for serving GLB
app.mount("/meshes", StaticFiles(directory=str(OUTPUT_DIR)), name="meshes")


class GenerateRequest(BaseModel):
    """Request model for geometry generation."""

    shoe_length_mm: float = Field(..., ge=250, le=330, description="Shoe length in mm")
    shoe_width_mm: float = Field(..., ge=90, le=130, description="Shoe width in mm")
    sole_thickness_mm: float = Field(..., ge=20, le=45, description="Sole thickness in mm")
    arch_height_mm: float = Field(..., ge=5, le=35, description="Arch height in mm")
    toe_spring_mm: float = Field(..., ge=5, le=25, description="Toe spring in mm")
    collar_height_mm: float = Field(..., ge=30, le=90, description="Collar height in mm")


class GenerateResponse(BaseModel):
    """Response model for generated geometry."""

    mesh_uri: str
    anchors_uri: str
    bounds: dict
    geometry_hash: str
    vertex_count: int
    face_count: int


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="healthy", version="1.0.0")


@app.post("/api/geometry/generate", response_model=GenerateResponse)
async def generate_geometry(request: GenerateRequest) -> GenerateResponse:
    """
    Generate 3D shoe geometry from instrumental specifications.

    Takes shoe dimensions and returns a GLB mesh file URI.
    """
    try:
        specs = InstrumentalSpecs(
            shoe_length_mm=request.shoe_length_mm,
            shoe_width_mm=request.shoe_width_mm,
            sole_thickness_mm=request.sole_thickness_mm,
            arch_height_mm=request.arch_height_mm,
            toe_spring_mm=request.toe_spring_mm,
            collar_height_mm=request.collar_height_mm,
        )

        logger.info(f"Generating geometry for hash: {specs.geometry_hash()}")

        result = generate_and_export(specs, OUTPUT_DIR)

        # Convert absolute paths to relative URIs for frontend
        mesh_filename = Path(result["mesh_uri"]).name
        anchors_filename = Path(result["anchors_uri"]).name

        return GenerateResponse(
            mesh_uri=f"/meshes/{mesh_filename}",
            anchors_uri=f"/meshes/{anchors_filename}",
            bounds=result["bounds"],
            geometry_hash=result["geometry_hash"],
            vertex_count=result["vertex_count"],
            face_count=result["face_count"],
        )

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@app.get("/api/geometry/{geometry_hash}")
async def get_geometry(geometry_hash: str) -> FileResponse:
    """
    Retrieve a previously generated geometry by hash.
    """
    glb_path = OUTPUT_DIR / f"{geometry_hash}.glb"

    if not glb_path.exists():
        raise HTTPException(status_code=404, detail=f"Geometry not found: {geometry_hash}")

    return FileResponse(
        path=str(glb_path),
        media_type="model/gltf-binary",
        filename=f"{geometry_hash}.glb",
    )


@app.get("/api/geometry/{geometry_hash}/anchors")
async def get_anchors(geometry_hash: str) -> dict:
    """
    Retrieve anchor points for a geometry.
    """
    import json

    anchors_path = OUTPUT_DIR / f"{geometry_hash}_anchors.json"

    if not anchors_path.exists():
        raise HTTPException(status_code=404, detail=f"Anchors not found: {geometry_hash}")

    with open(anchors_path) as f:
        return json.load(f)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
