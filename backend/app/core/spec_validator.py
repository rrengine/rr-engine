from typing import Dict, Any, List
from app.schemas.validation import ValidationState, ValidationIssue
from app.core.spec_requirements import INSTRUMENTAL_REQUIRED, NON_INSTRUMENTAL_CANONICAL

def _get(d: Dict[str, Any], path: List[str]):
    cur = d
    for p in path:
        if not isinstance(cur, dict) or p not in cur:
            return None, False
        cur = cur[p]
    return cur, True

def _validate_node(base: Dict[str, Any], req: Dict[str, Any], prefix: List[str], errors: List[ValidationIssue]):
    for key, rule in req.items():
        path = prefix + [key]
        if "type" in rule:
            val, ok = _get(base, path)
            if not ok:
                errors.append(ValidationIssue(
                    path=".".join(path),
                    issue="missing",
                    detail="Required instrumental spec is missing."
                ))
                continue
            if rule["type"] == "number":
                if not isinstance(val, (int, float)):
                    errors.append(ValidationIssue(
                        path=".".join(path),
                        issue="invalid_type",
                        detail="Expected number.",
                        received=type(val).__name__
                    ))
                    continue
                if "min" in rule and val < rule["min"]:
                    errors.append(ValidationIssue(
                        path=".".join(path),
                        issue="out_of_range",
                        detail="Value below minimum.",
                        min=rule["min"],
                        max=rule.get("max"),
                        received=val
                    ))
                if "max" in rule and val > rule["max"]:
                    errors.append(ValidationIssue(
                        path=".".join(path),
                        issue="out_of_range",
                        detail="Value above maximum.",
                        min=rule.get("min"),
                        max=rule["max"],
                        received=val
                    ))
        else:
            _validate_node(base, rule, path, errors)

def validate_specs(instrumental_specs: Dict[str, Any], non_instrumental_specs: Dict[str, Any] | None) -> ValidationState:
    instrumental_errors: List[ValidationIssue] = []
    _validate_node(instrumental_specs, INSTRUMENTAL_REQUIRED, [], instrumental_errors)

    missing_non_instrumental: List[str] = []
    non_inst = non_instrumental_specs or {}
    for section, fields in NON_INSTRUMENTAL_CANONICAL.items():
        for field in fields.keys():
            _, ok = _get(non_inst, [section, field])
            if not ok:
                missing_non_instrumental.append(f"{section}.{field}")

    is_blocking = len(instrumental_errors) > 0
    summary = "Blocking instrumental spec errors present." if is_blocking else "Instrumental specs valid."
    if missing_non_instrumental:
        summary += f" Missing {len(missing_non_instrumental)} non-instrumental fields."
    return ValidationState(
        is_blocking=is_blocking,
        instrumental_errors=instrumental_errors,
        missing_non_instrumental=missing_non_instrumental,
        summary=summary
    )
