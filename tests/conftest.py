"""Pytest configuration and fixtures"""

import pytest
from fastapi.testclient import TestClient

from fastapi_01.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)
