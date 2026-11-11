import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def test_activity(monkeypatch):
    activity = {
        "description": "Activity used for API tests",
        "schedule": "Fridays",
        "max_participants": 10,
        "participants": [],
    }
    monkeypatch.setitem(activities, "Test Activity", activity)
    return activity


def test_get_activities_returns_available_activities(client, test_activity):
    # Arrange
    expected_name = "Test Activity"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert expected_name in response.json()
    assert response.json()[expected_name] == test_activity


def test_signup_adds_participant(client, test_activity):
    # Arrange
    activity_name = "Test Activity"
    email = "student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in test_activity["participants"]


def test_signup_rejects_duplicate_participant(client, test_activity):
    # Arrange
    activity_name = "Test Activity"
    email = "student@mergington.edu"
    test_activity["participants"].append(email)

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"
    assert test_activity["participants"] == [email]


def test_signup_rejects_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Activity"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": "student@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant(client, test_activity):
    # Arrange
    activity_name = "Test Activity"
    email = "student@mergington.edu"
    test_activity["participants"].append(email)

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    assert email not in test_activity["participants"]


def test_unregister_rejects_unregistered_participant(client, test_activity):
    # Arrange
    activity_name = "Test Activity"
    email = "student@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
    assert test_activity["participants"] == []


def test_unregister_rejects_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Activity"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": "student@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
