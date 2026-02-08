"""
<!--
<ai_agent_documentation>
  <file_meta>
    <name>test_validation_metrics.py</name>
    <version>1.0.0</version>
    <type>unit_test</type>
    <purpose>Validate detection report metric normalization</purpose>
    <last_updated>2026-02-08</last_updated>
    <maintainer>ArUCO Generator Team</maintainer>
  </file_meta>
</ai_agent_documentation>
-->
Validation metrics unit tests
"""

from aruco_generator.validation import DetectionValidator


def test_detection_report_uses_ms_keys():
    validator = DetectionValidator()
    report = validator.generate_detection_report(
        [{"detected": True, "detection_time_ms": 12.5}],
        {"pattern_type": "unit"},
    )
    perf = report.get("performance", {})
    assert perf.get("avg_detection_time") == 12.5


def test_detection_report_falls_back_to_legacy_time():
    validator = DetectionValidator()
    report = validator.generate_detection_report(
        [{"detected": True, "detection_time": 8.0}],
        {"pattern_type": "unit"},
    )
    perf = report.get("performance", {})
    assert perf.get("avg_detection_time") == 8.0
