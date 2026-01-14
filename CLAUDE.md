# RR-ENGINE: Claude Code Configuration

## CRITICAL: Production-Grade Code Only

This project requires **production-ready implementations only**. The following are strictly prohibited:

### NEVER Generate:
- `# TODO:` comments as placeholders for real logic
- `pass` statements where implementation is needed
- `raise NotImplementedError()` without immediate implementation
- `...` (ellipsis) as placeholder code
- Mock/fake data generators (unless explicitly for tests)
- `print()` statements for debugging (use proper logging)
- Hardcoded credentials, secrets, or API keys
- `# placeholder`, `# stub`, `# mock` comments
- Functions that return static/dummy data pretending to be real
- Silent `try/except: pass` blocks that swallow errors
- `time.sleep()` as a fake async operation
- Comments like "implement later" or "add real logic here"
- Synthetic data masquerading as real implementation
- Fallback returns that hide missing functionality

### ALWAYS Provide:
- Complete, working implementations
- Proper error handling with meaningful messages
- Type hints on all function signatures
- Database migrations when schema changes
- Environment variable validation at startup
- Logging with appropriate levels (debug, info, warning, error)
- Input validation before processing
- Proper async/await patterns (no sync in async context)
- Connection pooling and resource cleanup
- Actual algorithms, not pseudocode

## Code Quality Standards

### Error Handling
```python
# WRONG - Silent failure
try:
    result = do_something()
except:
    pass

# CORRECT - Explicit handling
try:
    result = do_something()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    raise HTTPException(status_code=500, detail=str(e))
```

### Async Patterns
```python
# WRONG - Sync DB in async context
def get_user(db: Session, user_id: UUID):
    return db.query(User).filter(User.id == user_id).first()

# CORRECT - Async all the way
async def get_user(db: AsyncSession, user_id: UUID):
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()
```

### No Fake Implementations
```python
# WRONG - Fake geometry that pretends to work
def build_geometry(specs: dict) -> dict:
    return {"mesh_uri": "fake.glb", "status": "ok"}  # NEVER DO THIS

# CORRECT - Real implementation or explicit error
def build_geometry(specs: dict) -> dict:
    mesh = generate_shoe_mesh(
        length=specs["shoe_length_mm"],
        width=specs["shoe_width_mm"],
        sole_thickness=specs["sole_thickness_mm"]
    )
    uri = save_mesh_to_storage(mesh)
    return {"mesh_uri": uri, "bounds": mesh.bounds.tolist()}
```

## Project Architecture

### Tech Stack (Target)
- **API**: Go (Fiber) or Rust (Axum) - NOT Python for performance-critical paths
- **Geometry Engine**: Rust with wgpu or Trimesh (Python) for prototyping
- **Frontend**: React + React Three Fiber + Tailwind + shadcn/ui
- **Database**: PostgreSQL with proper connection pooling
- **Cache**: Redis for sessions, rate limiting, and hot data
- **AI Services**: Python microservice (isolated from main API)

### Directory Structure
```
rr-engine/
├── api/           # Go/Rust API server
├── geometry/      # Rust geometry engine (or Python+Trimesh during prototype)
├── frontend/      # React + R3F application
├── ai-service/    # Python AI/ML microservice
├── migrations/    # Database migrations
├── docs/          # Documentation
└── scripts/       # Build and deployment scripts
```

## Geometry Engine Requirements

The geometry engine MUST:
1. Accept instrumental specs (dimensions in mm)
2. Generate actual 3D mesh data (vertices, faces, normals)
3. Export to GLB/GLTF format
4. Compute deterministic geometry hash from specs
5. Support anchor point definitions for accessories
6. Calculate accurate bounding boxes

Libraries to use:
- Python prototype: `trimesh`, `numpy`, `pygltflib`
- Production: Rust with `glam`, `gltf`, custom mesh generation

## API Requirements

All endpoints MUST:
1. Validate input with proper schemas
2. Return appropriate HTTP status codes
3. Include request timing in response headers
4. Log all errors with context
5. Use connection pooling
6. Handle concurrent requests without blocking

## Testing Requirements

When tests are written, they MUST:
1. Test actual functionality, not mocks
2. Use real database (test container)
3. Verify actual file output for geometry
4. Include integration tests for API endpoints
5. Test error conditions explicitly

## Response Format

When I ask for implementation, provide:
1. Complete file contents (not snippets with `...`)
2. All imports at the top
3. All dependencies that need to be installed
4. Migration files if schema changes
5. Environment variables needed

## Pre-Implementation Checklist

Before writing any code, verify:
- [ ] Is this production-ready or a stub?
- [ ] Does it handle all error cases?
- [ ] Are there any `TODO` or placeholder comments?
- [ ] Is async/await used correctly?
- [ ] Are all dependencies real and installable?
- [ ] Will this work with real data at scale?

If any answer is "no" or "not sure", revise before presenting.

---

**Remember**: This is a fashion-tech platform that will generate real 3D assets for manufacturing. Every piece of code must work in production. No exceptions.
