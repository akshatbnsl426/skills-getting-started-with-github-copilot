import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture
def client(monkeypatch):
    test_activities = {
        "Chess Club": {
            "description": "Practice chess",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["student@example.com"],
        }
    }
    monkeypatch.setattr(app_module, "activities", test_activities)
    return TestClient(app_module.app)


def test_get_activities_returns_catalog(client):
    # Arrange
    expected_activity = {
        "description": "Practice chess",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["student@example.com"],
    }

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"Chess Club": expected_activity}


def test_signup_adds_student(client):
    # Arrange
    email = "new-student@example.com"

    # Act
    response = client.post("/activities/Chess%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in client.get("/activities").json()["Chess Club"]["participants"]


def test_signup_rejects_duplicate_student(client):
    # Arrange
    email = "student@example.com"

    # Act
    response = client.post("/activities/Chess%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert client.get("/activities").json()["Chess Club"]["participants"] == [email]


def test_signup_rejects_unknown_activity(client):
    # Arrange
    email = "new-student@example.com"

    # Act
    response = client.post("/activities/Missing%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 404


def test_unregister_removes_student(client):
    # Arrange
    email = "student@example.com"

    # Act
    response = client.delete("/activities/Chess%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}
    assert client.get("/activities").json()["Chess Club"]["participants"] == []


def test_unregister_rejects_student_not_registered(client):
    # Arrange
    email = "missing-student@example.com"

    # Act
    response = client.delete("/activities/Chess%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert client.get("/activities").json()["Chess Club"]["participants"] == [
        "student@example.com"
    ]


def test_unregister_rejects_unknown_activity(client):
    # Arrange
    email = "student@example.com"

    # Act
    response = client.delete("/activities/Missing%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 404