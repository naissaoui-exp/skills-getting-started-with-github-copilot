from __future__ import annotations

import copy

import pytest
from fastapi.testclient import TestClient

from app import activities, app


@pytest.fixture(autouse=True)
def restore_activities_state():
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_get_activities():
    client = TestClient(app)
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "schedule" in data["Chess Club"]


def test_signup_activity_adds_participant():
    client = TestClient(app)
    email = "newstudent@mergington.edu"
    activity = "Soccer Club"

    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert email in activities[activity]["participants"]


def test_signup_duplicate_is_rejected():
    client = TestClient(app)
    email = "dupstudent@mergington.edu"
    activity = "Basketball Club"

    first = client.post(
        f"/activities/{activity}/signup",
        params={"email": email},
    )
    second = client.post(
        f"/activities/{activity}/signup",
        params={"email": email},
    )

    assert first.status_code == 200
    assert second.status_code == 400
    assert second.json()["detail"] == "Student already signed up for this activity"


def test_unregister_removes_participant():
    client = TestClient(app)
    email = "remove@mergington.edu"
    activity = "Art Studio"

    signup = client.post(
        f"/activities/{activity}/signup",
        params={"email": email},
    )

    assert signup.status_code == 200

    unregister = client.delete(
        f"/activities/{activity}/participants",
        params={"email": email},
    )

    assert unregister.status_code == 200
    assert email not in activities[activity]["participants"]


def test_unregister_missing_participant_returns_404():
    client = TestClient(app)
    email = "missing@mergington.edu"
    activity = "Drama Club"

    response = client.delete(
        f"/activities/{activity}/participants",
        params={"email": email},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student not registered for this activity"
