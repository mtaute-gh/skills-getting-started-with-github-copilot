from urllib.parse import quote

from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_get_activities_returns_all_activities():
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    activities = response.json()
    assert expected_activity in activities
    assert isinstance(activities[expected_activity]["participants"], list)


def test_signup_for_activity_adds_participant():
    # Arrange
    activity_name = quote("Art Club", safe="")
    email = "pytest.new.participant@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Art Club"

    # Cleanup
    client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )


def test_signup_duplicate_returns_error():
    # Arrange
    activity_name = quote("Art Club", safe="")
    email = "pytest.duplicate.participant@mergington.edu"
    client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"

    # Cleanup
    client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )


def test_unregister_participant_removes_participant():
    # Arrange
    activity_name = quote("Debate Team", safe="")
    email = "pytest.unregister.participant@mergington.edu"
    client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from Debate Team"


def test_unregister_missing_participant_returns_404():
    # Arrange
    activity_name = quote("Debate Team", safe="")
    email = "pytest.missing.participant@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
