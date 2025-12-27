import cv2
import numpy as np

from aruco_generator.calibration import CalibrationPatternGenerator


def test_charuco_generation():
    """Test Charuco board generation"""
    generator = CalibrationPatternGenerator()

    # Generate board
    result = generator.generate_charuco_board(
        squares_x=5,
        squares_y=7,
        square_size_mm=30,
        marker_size_mm=22,
        dictionary="4X4_50",
    )

    assert result["image"] is not None
    assert result["dimensions_mm"] == (150.0, 210.0)
    assert result["calibration_data"]["pattern_type"] == "charuco"

    # Verify image properties
    img = result["image"]
    assert len(img.shape) == 2 or img.shape[2] == 1  # Grayscale
    assert img.dtype == np.uint8

    # Try to detect it back using Aruco
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)

    # In OpenCV 4.7+, Charuco detection is slightly different
    # But let's just use ArucoDetector to check markers
    detector = cv2.aruco.ArucoDetector(dictionary)
    corners, ids, _ = detector.detectMarkers(img)

    # Should detect markers
    assert len(ids) > 0
    print(f"Successfully detected {len(ids)} markers on generated Charuco board")


if __name__ == "__main__":
    test_charuco_generation()
