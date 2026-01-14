from fastapi import FastAPI
from app.api.projects import router as projects_router
from app.api.generations import router as generations_router
from app.api.validate import router as validate_router
from app.api.generate import router as generate_router
from app.api.imports import router as import_router
from app.api.exports import router as export_router
from app.api.factory_feedback import router as factory_feedback_router

app = FastAPI(title="RR System v1")

app.include_router(projects_router)
app.include_router(generations_router)
app.include_router(validate_router)
app.include_router(generate_router)
app.include_router(import_router)
app.include_router(export_router)
app.include_router(factory_feedback_router)

@app.get("/health")
def health():
    return {"ok": True}
