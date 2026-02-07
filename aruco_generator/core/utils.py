"""
<!--
<ai_agent_documentation>
  <file_meta>
    <name>utils.py</name>
    <version>1.1.0</version>
    <type>core_utility_module</type>
    <purpose>Shared validation, error handling helpers, and API response shaping</purpose>
    <last_updated>2026-02-07</last_updated>
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
from typing import Any, Dict, Optional

from flask import current_app, g, has_request_context, jsonify, request

logger = logging.getLogger(__name__)


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
        raise ValueError("Request body must be a JSON object")

    dictionary = data.get("dictionary")
    if not dictionary or dictionary not in available_dictionaries:
        # Provide a helpful error message with a few suggestions
        suggestions = ", ".join(available_dictionaries[:5])
        if len(available_dictionaries) > 5:
            suggestions += "..."
        raise ValueError(f'Invalid dictionary "{dictionary}". Available: {suggestions}')

    try:
        start_id = int(data.get("start_id", 0))
        if start_id < 0:
            raise ValueError("Start ID must be non-negative")

        rows = int(data.get("rows", 1))
        cols = int(data.get("cols", 1))
        if rows <= 0 or cols <= 0:
            raise ValueError("Rows and columns must be positive integers")

        size_mm = float(data.get("size_mm", 20))
        if size_mm <= 0:
            raise ValueError("Marker size must be positive (in millimeters)")

        spacing_mm = float(data.get("spacing_mm", 5))
        if spacing_mm < 0:
            raise ValueError("Spacing must be non-negative (in millimeters)")

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
        }

    except (TypeError, ValueError) as e:
        # Catch basic casting errors if not caught above
        if "invalid literal" in str(e):
            raise ValueError("Invalid number format for one of the parameters")
        raise e


def handle_api_errors(f):
    """Decorator to standardize API error handling."""

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            path = request.path if has_request_context() else "unknown"
            logger.warning(
                "API validation error in %s | request_id=%s path=%s message=%s",
                f.__name__,
                getattr(g, "request_id", "unknown"),
                path,
                str(e),
            )
            return jsonify(_build_error_payload(str(e), 400, "validation_error")), 400
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
) -> Dict[str, Any]:
    path = request.path if has_request_context() else None
    method = request.method if has_request_context() else None
    payload = {
        "error": message,
        "type": error_type,
        "status": status,
        "request_id": getattr(g, "request_id", None),
        "path": path,
        "method": method,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if details:
        payload["details"] = details
    return payload


def _include_error_details() -> bool:
    try:
        if current_app.debug:
            return True
        return current_app.config.get("INCLUDE_ERROR_DETAILS", False)
    except Exception:
        return False
