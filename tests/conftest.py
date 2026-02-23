"""
<!--
<ai_agent_documentation>
  <file_meta>
    <name>conftest.py</name>
    <version>1.0.0</version>
    <type>test_fixtures</type>
    <purpose>Shared pytest fixtures for app, client, and database setup</purpose>
    <last_updated>2026-02-23</last_updated>
    <maintainer>ArUCO Generator Team</maintainer>
  </file_meta>
</ai_agent_documentation>
-->
"""

import pytest

from app import app as flask_app
from app import db as database


@pytest.fixture(scope="session")
def app():
    """Provide a configured Flask app for tests."""
    flask_app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
    )
    return flask_app


@pytest.fixture()
def client(app):
    """Provide a Flask test client with an initialized database."""
    with app.test_client() as client:
        with app.app_context():
            database.create_all()
        yield client
        with app.app_context():
            database.session.remove()
            database.drop_all()


@pytest.fixture()
def db(app):
    """Provide a database fixture for tests that need direct access."""
    with app.app_context():
        database.create_all()
        yield database
        database.session.remove()
        database.drop_all()
