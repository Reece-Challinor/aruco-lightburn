"""
<!--
<ai_agent_documentation>
  <file_meta>
    <name>utils.py</name>
    <version>1.3.0</version>
    <type>core_utility_module</type>
    <purpose>Shared validation, export-option handling, and API response shaping</purpose>
    <last_updated>2026-08-01</last_updated>
    <maintainer>ArUCO Generator Team</maintainer>
  </file_meta>
</ai_agent_documentation>
-->
Utility functions for ArUCO Generator.
Contains shared validation logic and error handling decorators.
"""

import functools
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from flask import current_app, g, has_request_context, jsonify, request
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)


class APIValidationError(ValueError):
    """Validation error with optional field-level details."""

    def __init__(
        self,
        message: str,
        *,
        fields: Optional[Dict[str, str]] = None,
        suggestions: Optional[List[str]] = None,
        status: int = 400,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.fields = fields or {}
        self.suggestions = suggestions or []
        self.status = status


class APIServiceUnavailableError(RuntimeError):
    """Service unavailable error (e.g., missing OpenCV)."""

    def __init__(self, message: str, *, status: int = 503) -> None:
        super().__init__(message)
        self.message = message
        self.status = status


def validate_generation_params(
    data: Dict[str, Any], available_dictionaries: list
) -> Dict[str, Any]:
    """
    Validate and extract common generation parameters.

    Args:
        data: Request JSON data or args
        available_dictionaries: List of valid dictionary names

    Returns:
        Dict with validated and casted parameters

    Raises:
        ValueError: If validation fails
    """
    if not isinstance(data, dict):
        raise APIValidationError("Request body must be a JSON object")

    dictionary = data.get("dictionary")
    if not dictionary or dictionary not in available_dictionaries:
        # Provide a helpful error message with a few suggestions
        suggestions = available_dictionaries[:5]
        hint = ", ".join(suggestions) + (
            "..." if len(available_dictionaries) > 5 else ""
        )
        raise APIValidationError(
            f'Invalid dictionary "{dictionary}". Available: {hint}',
            fields={"dictionary": "Select a valid dictionary name"},
            suggestions=suggestions,
        )

    try:
        start_id = int(data.get("start_id", 0))
        if start_id < 0:
            raise APIValidationError(
                "Start ID must be non-negative", fields={"start_id": "Must be >= 0"}
            )

        rows = int(data.get("rows", 1))
        cols = int(data.get("cols", 1))
        if rows <= 0:
            raise APIValidationError(
                "Rows must be a positive integer", fields={"rows": "Must be >= 1"}
            )
        if cols <= 0:
            raise APIValidationError(
                "Columns must be a positive integer", fields={"cols": "Must be >= 1"}
            )

        size_mm = float(data.get("size_mm", 20))
        if size_mm <= 0:
            raise APIValidationError(
                "Marker size must be positive (in millimeters)",
                fields={"size_mm": "Must be > 0"},
            )

        spacing_mm = float(data.get("spacing_mm", 5))
        if spacing_mm < 0:
            raise APIValidationError(
                "Spacing must be non-negative (in millimeters)",
                fields={"spacing_mm": "Must be >= 0"},
            )

        border_bits = int(data.get("border_bits", 1))

        return {
            "dictionary": dictionary,
            "start_id": start_id,
            "rows": rows,
            "cols": cols,
            "size_mm": size_mm,
            "spacing_mm": spacing_mm,
            "border_bits": border_bits,
            "include_borders": data.get("include_borders", True),
            "include_outer_border": data.get("include_outer_border", False),
            "include_labels": data.get("include_labels", False),
            "border_width": float(data.get("border_width", 2.0)),
            # Pass through other potential params
            "include_alignment": data.get("include_alignment", False),
            "include_rulers": data.get("include_rulers", False),
            # Print exports carry the F-07a scale check by default. Callers
            # may explicitly disable it, while preview and cut routes ignore it.
            "include_ruler": bool(data.get("include_ruler", True)),
        }

    except APIValidationError:
        raise
    except (TypeError, ValueError) as e:
        # Catch basic casting errors if not caught above
        if "invalid literal" in str(e):
            raise APIValidationError("Invalid number format for one of the parameters")
        raise APIValidationError(str(e))


def handle_api_errors(f):
    """Decorator to standardize API error handling."""

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except APIValidationError as e:
            path = request.path if has_request_context() else "unknown"
            logger.warning(
                "API validation error in %s | request_id=%s path=%s message=%s",
                f.__name__,
                getattr(g, "request_id", "unknown"),
                path,
                e.message,
            )
            return (
                jsonify(
                    _build_error_payload(
                        e.message,
                        e.status,
                        "validation_error",
                        fields=e.fields,
                        suggestions=e.suggestions,
                    )
                ),
                e.status,
            )
        except ValueError as e:
            path = request.path if has_request_context() else "unknown"
            logger.warning(
                "API validation error in %s | request_id=%s path=%s message=%s",
                f.__name__,
                getattr(g, "request_id", "unknown"),
                path,
                str(e),
            )
            return (
                jsonify(_build_error_payload(str(e), 400, "validation_error")),
                400,
            )
        except APIServiceUnavailableError as e:
            path = request.path if has_request_context() else "unknown"
            logger.warning(
                "API service unavailable in %s | request_id=%s path=%s message=%s",
                f.__name__,
                getattr(g, "request_id", "unknown"),
                path,
                e.message,
            )
            return (
                jsonify(
                    _build_error_payload(
                        e.message,
                        e.status,
                        "service_unavailable",
                        suggestions=["Install OpenCV to enable this feature"],
                    )
                ),
                e.status,
            )
        except RuntimeError as e:
            if "OpenCV required" in str(e):
                return (
                    jsonify(
                        _build_error_payload(
                            "OpenCV is required for this operation.",
                            503,
                            "service_unavailable",
                            suggestions=["Install OpenCV to enable this feature"],
                        )
                    ),
                    503,
                )
            path = request.path if has_request_context() else "unknown"
            logger.error(
                "API Runtime error in %s | request_id=%s path=%s",
                f.__name__,
                getattr(g, "request_id", "unknown"),
                path,
                exc_info=True,
            )
            details = str(e) if _include_error_details() else None
            return (
                jsonify(
                    _build_error_payload(
                        "Internal server error. Please check your parameters.",
                        500,
                        "internal_error",
                        details=details,
                    )
                ),
                500,
            )
        except HTTPException as e:
            status_code = e.code or 404
            error_type = "payload_too_large" if status_code == 413 else "http_error"
            fields = {"file": "File too large"} if status_code == 413 else None
            return (
                jsonify(
                    _build_error_payload(
                        e.description or "Resource not found",
                        status_code,
                        error_type,
                        fields=fields,
                    )
                ),
                status_code,
            )
        except Exception as e:
            path = request.path if has_request_context() else "unknown"
            logger.error(
                "API Error in %s | request_id=%s path=%s",
                f.__name__,
                getattr(g, "request_id", "unknown"),
                path,
                exc_info=True,
            )
            details = str(e) if _include_error_details() else None
            return (
                jsonify(
                    _build_error_payload(
                        "Internal server error. Please check your parameters.",
                        500,
                        "internal_error",
                        details=details,
                    )
                ),
                500,
            )

    return wrapper


def _build_error_payload(
    message: str,
    status: int,
    error_type: str,
    details: Optional[str] = None,
    fields: Optional[Dict[str, str]] = None,
    suggestions: Optional[List[str]] = None,
) -> Dict[str, Any]:
    path = request.path if has_request_context() else None
    method = request.method if has_request_context() else None
    error_payload: Dict[str, Any] = {
        "message": message,
        "type": error_type,
        "status": status,
    }
    if fields:
        error_payload["fields"] = fields
    if suggestions:
        error_payload["suggestions"] = suggestions
    if details:
        error_payload["details"] = details

    return {
        "success": False,
        "error": error_payload,
        "request_id": getattr(g, "request_id", None),
        "path": path,
        "method": method,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": _get_app_version(),
    }


def build_error_payload(
    message: str,
    status: int,
    error_type: str,
    *,
    details: Optional[str] = None,
    fields: Optional[Dict[str, str]] = None,
    suggestions: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Public wrapper for standardized error payloads."""
    return _build_error_payload(
        message,
        status,
        error_type,
        details=details,
        fields=fields,
        suggestions=suggestions,
    )


def api_success(
    data: Optional[Dict[str, Any]] = None,
    *,
    warnings: Optional[List[Dict[str, str]]] = None,
    status: int = 200,
) -> tuple:
    payload = {
        "success": True,
        "data": data or {},
        "warnings": warnings or [],
        "request_id": getattr(g, "request_id", None),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": _get_app_version(),
    }
    return jsonify(payload), status


def _get_app_version() -> Optional[str]:
    try:
        return current_app.config.get("APP_VERSION")
    except Exception:
        return None


def _include_error_details() -> bool:
    try:
        if current_app.debug:
            return True
        return current_app.config.get("INCLUDE_ERROR_DETAILS", False)
    except Exception:
        return False
