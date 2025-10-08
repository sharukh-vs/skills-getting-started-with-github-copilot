from fastapi.testclient import TestClient
import pytest

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    # Reset the in-memory activities before each test to a known state
    # We'll deep-copy the initial state from the module-level activities template
    initial = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        }
    }
    activities.clear()
    activities.update(initial)
    yield


def test_get_activities():
    client = TestClient(app)
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"].get("participants"), list)


def test_signup_and_duplicate():
    client = TestClient(app)

    # sign up a new participant
    resp = client.post("/activities/Chess%20Club/signup?email=newstudent@mergington.edu")
    assert resp.status_code == 200
    assert resp.json()["message"].startswith("Signed up newstudent@mergington.edu")

    # verify participant added
    resp = client.get("/activities")
    participants = resp.json()["Chess Club"]["participants"]
    assert "newstudent@mergington.edu" in participants

    # duplicate signup should return 400
    resp = client.post("/activities/Chess%20Club/signup?email=newstudent@mergington.edu")
    assert resp.status_code == 400


def test_remove_participant_and_errors():
    client = TestClient(app)

    # remove existing participant
    resp = client.delete("/activities/Chess%20Club/participants?email=michael@mergington.edu")
    assert resp.status_code == 200
    assert resp.json()["message"].startswith("Removed michael@mergington.edu")

    # removing again should 404
    resp = client.delete("/activities/Chess%20Club/participants?email=michael@mergington.edu")
    assert resp.status_code == 404

    # removing from non-existent activity should 404
    resp = client.delete("/activities/Nope/participants?email=someone@x.com")
    assert resp.status_code == 404
