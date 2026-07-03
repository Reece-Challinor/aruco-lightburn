"""
Simplified database models for ArUCO Generator

<!--
<ai_agent_documentation>
  <file_meta>
    <name>models.py</name>
    <version>4.0.0</version>
    <type>sqlalchemy_models</type>
    <purpose>Database schema definitions for calibration patterns (FROZEN surface — see F-10)</purpose>
    <last_updated>2026-07-03</last_updated>
  </file_meta>

  <golden_path>
    <description>Database models usage</description>
    <steps>
      <step id="1">Import db from extensions</step>
      <step id="2">Define models inheriting from db.Model</step>
      <step id="3">Use to_dict for JSON serialization</step>
    </steps>
  </golden_path>
</ai_agent_documentation>
"""

from datetime import datetime, timezone

from flask_login import UserMixin
from sqlalchemy import JSON

from .extensions import db


def _utcnow() -> datetime:
    """Timezone-aware replacement for the deprecated datetime.utcnow."""
    return datetime.now(timezone.utc)


class User(UserMixin, db.Model):
    """User model for authentication (if needed in future)"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=_utcnow)

    def to_dict(self):
        """Convert user to dictionary"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "is_admin": self.is_admin,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class CalibrationPattern(db.Model):
    """Store generated calibration patterns and ArUCO markers

    FROZEN (roadmap F-10, 2026-07-03): pattern persistence is kept for
    backward compatibility but gains no new capabilities. In serverless
    production the DB is per-invocation in-memory, so persistence surfaces
    must not be extended. DetectionMetric was removed entirely.
    """

    __tablename__ = "calibration_patterns"
    __table_args__ = (
        db.Index("ix_calibration_patterns_created_at", "created_at"),
        db.Index("ix_calibration_patterns_type", "pattern_type"),
        db.Index("ix_calibration_patterns_dictionary", "dictionary_type"),
    )

    id = db.Column(db.Integer, primary_key=True)
    pattern_type = db.Column(
        db.String(50), nullable=False
    )  # 'aruco_marker', 'charuco', 'aruco_board'
    pattern_name = db.Column(db.String(200))  # User-defined name

    # Physical dimensions
    physical_width_mm = db.Column(db.Float, nullable=False)
    physical_height_mm = db.Column(db.Float, nullable=False)
    marker_size_mm = db.Column(db.Float)

    # Pattern parameters
    grid_size_x = db.Column(db.Integer)  # Number of markers in X
    grid_size_y = db.Column(db.Integer)  # Number of markers in Y
    dictionary_type = db.Column(db.String(50))  # ARUCO dictionary type
    total_markers = db.Column(db.Integer)
    first_marker_id = db.Column(db.Integer, default=0)

    # Store generation parameters as JSON
    calibration_data = db.Column(JSON, nullable=False)

    # Metadata
    created_at = db.Column(db.DateTime, default=_utcnow, nullable=False)
    notes = db.Column(db.Text)
    image_checksum = db.Column(db.String(64))  # SHA256 checksum of generated image

    def __repr__(self):
        return (
            f"<CalibrationPattern {self.id}: {self.pattern_type} - {self.pattern_name}>"
        )

    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "pattern_type": self.pattern_type,
            "pattern_name": self.pattern_name,
            "physical_width_mm": self.physical_width_mm,
            "physical_height_mm": self.physical_height_mm,
            "marker_size_mm": self.marker_size_mm,
            "grid_size": [self.grid_size_x, self.grid_size_y],
            "dictionary_type": self.dictionary_type,
            "total_markers": self.total_markers,
            "first_marker_id": self.first_marker_id,
            "image_checksum": self.image_checksum,
            "calibration_data": self.calibration_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
