from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

BASE_ACTIVITIES = deepcopy(activities)
client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(deepcopy(BASE_ACTIVITIES))
    yield
    activities.clear()
    activities.update(deepcopy(BASE_ACTIVITIES))


def test_get_activities_returns_activity_data():
    # Arrange
    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"], dict)
    assert data["Chess Club"]["description"].startswith("Learn strategies")
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_adds_participant_to_activity():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    refresh = client.get("/activities")
    participants = refresh.json()[activity_name]["participants"]
    assert email in participants


def test_signup_duplicate_participant_returns_bad_request():
    # Arrange
    activity_name = "Programming Class"
    email = "emma@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_remove_participant_from_activity():
    # Arrange
    activity_name = "Gym Class"
    email = "john@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"

    refresh = client.get("/activities")
    participants = refresh.json()[activity_name]["participants"]
    assert email not in participants


def test_remove_missing_participant_returns_not_found():
    # Arrange
    activity_name = "Science Bowl"
    email = "unknown@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
