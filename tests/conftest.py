"""
Pytest configuration and fixtures for FastAPI tests.
"""

import pytest
import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fastapi.testclient import TestClient
from app import app


@pytest.fixture
def client():
    """
    Fixture that provides a TestClient instance for making requests to the FastAPI app.
    
    Arrange: Initialize the test client
    """
    return TestClient(app)


@pytest.fixture
def sample_email():
    """
    Fixture that provides a sample student email for testing.
    """
    return "test.student@mergington.edu"


@pytest.fixture
def existing_activity():
    """
    Fixture that provides the name of an activity that exists in the app.
    """
    return "Chess Club"


@pytest.fixture
def nonexistent_activity():
    """
    Fixture that provides the name of an activity that does not exist.
    """
    return "Underwater Basket Weaving Club"
