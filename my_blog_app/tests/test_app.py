# tests/test_app.py

import pytest
from app import app as flask_app # Import your Flask app instance

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # You might want to configure the app for testing here
    # e.g., using a separate test database or config
    flask_app.config.update({
        "TESTING": True,
        # Add other test-specific configurations if needed
        # "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:", # Example for DB
    })
    yield flask_app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

def test_index_page_loads(client):
    """Test if the index page (/) loads successfully."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Welcome to My Blog App!" in response.data # Check for specific content

