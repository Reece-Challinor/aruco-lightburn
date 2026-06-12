"""Vercel serverless entry point.

All routes are rewritten here (see vercel.json). The repo root is added to
sys.path so the top-level Flask app factory and aruco_generator package
resolve when Vercel executes from api/.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import app  # noqa: E402,F401
