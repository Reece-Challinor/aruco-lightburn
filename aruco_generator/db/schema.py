"""
Database schema validation and lightweight migration helpers.

<!--
<ai_agent_documentation>
  <file_meta>
    <name>schema.py</name>
    <version>1.0.0</version>
    <type>db_schema_helper</type>
    <purpose>Ensure database schema stays aligned with current models</purpose>
    <last_updated>2026-02-08</last_updated>
    <maintainer>ArUCO Generator Team</maintainer>
  </file_meta>
</ai_agent_documentation>
-->
"""

from __future__ import annotations

import logging

from sqlalchemy import inspect, text

from .models import CalibrationPattern

logger = logging.getLogger(__name__)


LEGACY_COLUMN_MAP = {
    "calibration_patterns": {
        "pattern_name": "name",
        "dictionary_type": "dictionary",
        "calibration_data": "pattern_data",
    }
}


def ensure_schema(db) -> None:
    """Ensure required columns exist and backfill legacy columns."""
    engine = db.engine
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())

    if "calibration_patterns" not in tables:
        return

    _ensure_columns(engine, inspector, CalibrationPattern.__table__)

    _backfill_legacy_columns(engine, inspector)


def _ensure_columns(engine, inspector, table) -> None:
    existing = {col["name"] for col in inspector.get_columns(table.name)}
    for column in table.columns:
        if column.name in existing or column.primary_key:
            continue
        column_type = column.type.compile(engine.dialect)
        ddl = f"ALTER TABLE {table.name} ADD COLUMN {column.name} {column_type}"
        logger.info("Applying schema patch: %s", ddl)
        with engine.begin() as conn:
            conn.execute(text(ddl))


def _backfill_legacy_columns(engine, inspector) -> None:
    columns = {col["name"] for col in inspector.get_columns("calibration_patterns")}
    legacy_map = LEGACY_COLUMN_MAP.get("calibration_patterns", {})
    for new_col, legacy_col in legacy_map.items():
        if new_col in columns and legacy_col in columns:
            sql = (
                f"UPDATE calibration_patterns "  # nosec B608 - controlled columns
                f"SET {new_col} = {legacy_col} "
                f"WHERE {new_col} IS NULL"
            )
            logger.info("Backfilling legacy column %s -> %s", legacy_col, new_col)
            with engine.begin() as conn:
                conn.execute(text(sql))
