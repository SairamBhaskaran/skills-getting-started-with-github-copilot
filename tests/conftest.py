"""
Pytest configuration and fixtures for FastAPI tests.

This module provides shared fixtures for test setup and teardown,
including test client initialization and activities state reset.
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path to enable imports from src.app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """
    Fixture that provides a TestClient instance for making HTTP requests
    to the FastAPI application.
    """
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """
    Fixture that resets the activities dictionary to its initial state
    before each test.
    
    This ensures test isolation and prevents state from leaking between tests.
    Autouse=True means this fixture runs before every test automatically.
    """
    # Store the original activities data
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball team with practice and games",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn tennis skills and compete in friendly matches",
            "schedule": "Saturdays, 10:00 AM - 11:30 AM",
            "max_participants": 16,
            "participants": ["isabella@mergington.edu"]
        },
        "Debate Club": {
            "description": "Develop critical thinking and public speaking skills",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["lucas@mergington.edu", "noah@mergington.edu"]
        },
        "Science Olympiad": {
            "description": "Compete in science competitions and build practical skills",
            "schedule": "Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 14,
            "participants": ["ava@mergington.edu"]
        },
        "Art Class": {
            "description": "Learn painting, drawing, and other visual arts techniques",
            "schedule": "Tuesdays and Thursdays, 4:45 PM - 5:45 PM",
            "max_participants": 20,
            "participants": ["mia@mergington.edu", "charlotte@mergington.edu"]
        },
        "Music Band": {
            "description": "Join the school band and perform at concerts and events",
            "schedule": "Mondays and Fridays, 3:30 PM - 4:30 PM",
            "max_participants": 25,
            "participants": ["ethan@mergington.edu"]
        }
    }
    
    # Clear and repopulate the activities dictionary
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Cleanup after test (optional, but good practice)
    activities.clear()
    activities.update(original_activities)
