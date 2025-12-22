"""
Shared extensions for the ArUCO Generator application.
Initializing extensions here avoids circular import issues between app.py and models.py.
"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Initialize database extension
db = SQLAlchemy(model_class=Base)
