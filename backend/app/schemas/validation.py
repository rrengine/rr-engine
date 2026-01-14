from pydantic import BaseModel
from typing import List, Any

class ValidationIssue(BaseModel):
    path: str
    issue: str
    detail: str
    min: float | None = None
    max: float | None = None
    received: Any | None = None

class ValidationState(BaseModel):
    is_blocking: bool
    instrumental_errors: List[ValidationIssue]
    missing_non_instrumental: List[str]
    summary: str
