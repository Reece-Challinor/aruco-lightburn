"""
Utility functions for ArUCO Generator.
Contains shared validation logic and error handling decorators.
"""

import functools
import logging
from typing import Any, Dict

from flask import jsonify

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
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            logger.error(f"API Error in {f.__name__}: {str(e)}", exc_info=True)
            return (
                jsonify(
                    {"error": "Internal server error. Please check your parameters."}
                ),
                500,
            )

    return wrapper
