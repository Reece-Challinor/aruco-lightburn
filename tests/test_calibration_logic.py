import cv2
import numpy as np

from aruco_generator.calibration import CalibrationPatternGenerator


def test_calibrate_camera_synthetic():
    """
    Test camera calibration with synthetically generated checkerboard images.
    """
    tools = CalibrationPatternGenerator()
    pattern_size = (9, 6)  # Internal corners
    square_size = 50  # pixels in generated image

    # Create local checkerboard generator
    def create_checkerboard(shape, square_size):
        params_width = shape[0] * square_size
        params_height = shape[1] * square_size
        img = np.zeros((params_height, params_width), dtype=np.uint8)
        for i in range(shape[1]):
            for j in range(shape[0]):
                if (i + j) % 2 == 0:
                    y1, y2 = i * square_size, (i + 1) * square_size
                    x1, x2 = j * square_size, (j + 1) * square_size
                    img[y1:y2, x1:x2] = 255
        # Add white border
        return cv2.copyMakeBorder(img, 20, 20, 20, 20, cv2.BORDER_CONSTANT, value=255)

    base_pattern = create_checkerboard((10, 7), square_size)

    # Create synthetic views
    images = []

    height, width = base_pattern.shape

    # 1. Original view
    images.append(base_pattern)

    # 2. Rotated view (perspective transform)
    src_pts = np.float32([[0, 0], [width, 0], [width, height], [0, height]])
    dst_pts = np.float32(
        [[0, 0], [width * 0.8, height * 0.1], [width * 0.8, height * 0.9], [0, height]]
    )
    M = cv2.getPerspectiveTransform(src_pts, dst_pts)
    warped1 = cv2.warpPerspective(base_pattern, M, (width, height))
    images.append(warped1)

    # 3. Another rotated view
    dst_pts2 = np.float32(
        [
            [width * 0.2, height * 0.1],
            [width, 0],
            [width, height],
            [width * 0.2, height * 0.9],
        ]
    )
    M2 = cv2.getPerspectiveTransform(src_pts, dst_pts2)
    warped2 = cv2.warpPerspective(base_pattern, M2, (width, height))
    images.append(warped2)
    # We need minimum 3 images
    # Let's check if findChessboardCorners works on these
    valid_images = []
    for img in [base_pattern, warped1, warped2]:
        ret, _ = cv2.findChessboardCorners(img, pattern_size, None)
        if ret:
            valid_images.append(img)

    assert len(valid_images) >= 3, "Failed to generate detectable synthetic images"

    # Run calibration
    result = tools.calibrate_camera(valid_images, pattern_size, square_size_mm=25.0)

    assert result["calibrated"] is True
    assert "camera_matrix" in result
    assert "distortion_coefficients" in result
    assert result["images_used"] >= 3
    print(f"Calibration successful with RMS error: {result['rms_error']}")


if __name__ == "__main__":
    test_calibrate_camera_synthetic()
