"""
<!--
<ai_agent_documentation>
  <file_meta>
    <name>test_utils.py</name>
    <version>1.2.0</version>
    <type>unit_test</type>
    <purpose>Validate core utility helpers and error handling</purpose>
    <last_updated>2026-02-23</last_updated>
    <maintainer>ArUCO Generator Team</maintainer>
  </file_meta>
</ai_agent_documentation>
-->
Unit tests for utility functions
"""

import os
import sys
import unittest

from flask import Flask

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from aruco_generator.core.utils import (  # noqa: E402
    handle_api_errors,
    validate_generation_params,
)


class TestUtils(unittest.TestCase):
    """Test utility functions"""

    def test_validate_generation_params_valid(self):
        """Test validation with valid data"""
        data = {"dictionary": "4X4_50", "start_id": "0", "rows": "2", "size_mm": "25.5"}
        available = ["4X4_50", "5X5_100"]

        result = validate_generation_params(data, available)

        self.assertEqual(result["dictionary"], "4X4_50")
        self.assertEqual(result["start_id"], 0)
        self.assertEqual(result["rows"], 2)
        self.assertEqual(result["size_mm"], 25.5)
        self.assertEqual(result["cols"], 1)  # Default
        self.assertEqual(result["spacing_mm"], 5.0)  # Default

    def test_validate_generation_params_invalid_dict(self):
        """Test validation with invalid dictionary"""
        data = {"dictionary": "INVALID"}
        available = ["4X4_50"]

        with self.assertRaises(ValueError) as cm:
            validate_generation_params(data, available)
        self.assertIn("Invalid dictionary", str(cm.exception))

    def test_validate_generation_params_invalid_numeric(self):
        """Test validation with invalid numeric values"""
        data = {"dictionary": "4X4_50", "rows": "-5"}  # Invalid negative
        available = ["4X4_50"]

        with self.assertRaises(ValueError):
            validate_generation_params(data, available)

    def test_handle_api_errors_decorator(self):
        """Test error handling decorator"""
        app = Flask(__name__)

        @handle_api_errors
        def success_func():
            return "Success"

        @handle_api_errors
        def value_error_func():
            raise ValueError("Bad input")

        @handle_api_errors
        def data_error_func():
            raise TypeError("Wrong type")  # Generic exception

        with app.app_context():
            # Test success
            self.assertEqual(success_func(), "Success")

            # Test ValueError (400)
            resp, code = value_error_func()
            self.assertEqual(code, 400)
            self.assertIn("Bad input", resp.get_json()["error"]["message"])

            # Test Generic Exception (500)
            resp, code = data_error_func()
            self.assertEqual(code, 500)
            self.assertIn("Internal server error", resp.get_json()["error"]["message"])


if __name__ == "__main__":
    unittest.main()
