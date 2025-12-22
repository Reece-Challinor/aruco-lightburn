"""
Unit tests for BatchGenerator
"""

import os
import sys
import unittest
import zipfile
from io import BytesIO

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from aruco_generator.batch import BatchGenerator  # noqa: E402


class TestBatchGenerator(unittest.TestCase):
    """Test batch generation functionality"""

    def setUp(self):
        self.batch_gen = BatchGenerator()
        self.base_config = {
            "dictionary": "4X4_50",
            "size_mm": 20,
            "spacing_mm": 5,
            "include_borders": True,
            "include_labels": True,
        }

    def test_calculate_optimal_grid(self):
        """Test grid optimization logic"""
        # Perfect squares
        self.assertEqual(self.batch_gen._calculate_optimal_grid(1), (1, 1))
        self.assertEqual(self.batch_gen._calculate_optimal_grid(4), (2, 2))
        self.assertEqual(self.batch_gen._calculate_optimal_grid(9), (3, 3))

        # Rectangular fits
        self.assertEqual(
            self.batch_gen._calculate_optimal_grid(2), (1, 2)
        )  # 1 row, 2 cols (landscape)
        self.assertEqual(
            self.batch_gen._calculate_optimal_grid(6), (2, 3)
        )  # 2 rows, 3 cols
        self.assertEqual(
            self.batch_gen._calculate_optimal_grid(12), (3, 4)
        )  # 3 rows, 4 cols

    def test_generate_batch_files(self):
        """Test generating a batch of files"""
        batch_size = 2
        markers_per_file = 4

        # Should generate 2 files with 4 markers each
        # Total markers: 8 (IDs 0-7)
        zip_buffer = self.batch_gen.generate_batch_files(
            self.base_config, batch_size, markers_per_file
        )

        self.assertIsInstance(zip_buffer, BytesIO)

        # Verify zip content
        with zipfile.ZipFile(zip_buffer, "r") as z:
            file_list = z.namelist()

            # Check for LightBurn files
            lbrn_files = [f for f in file_list if f.endswith(".lbrn2")]
            self.assertEqual(len(lbrn_files), 2)

            # Check for summary file
            self.assertIn("BATCH_SUMMARY.txt", file_list)

    def test_generate_id_sequence_files(self):
        """Test generating files from specific ID ranges"""
        ranges = [
            {"start": 0, "end": 4},  # 5 markers
            {"start": 10, "end": 14},  # 5 markers
        ]

        zip_buffer = self.batch_gen.generate_id_sequence_files(self.base_config, ranges)

        with zipfile.ZipFile(zip_buffer, "r") as z:
            file_list = z.namelist()
            lbrn_files = [f for f in file_list if f.endswith(".lbrn2")]
            self.assertEqual(len(lbrn_files), 2)

            # Check filename content for ID ranges
            self.assertTrue(any("0-4" in f for f in lbrn_files))
            self.assertTrue(any("10-14" in f for f in lbrn_files))


if __name__ == "__main__":
    unittest.main()
