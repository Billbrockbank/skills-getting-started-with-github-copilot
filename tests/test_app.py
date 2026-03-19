from src.app import activities


def test_root_redirects_to_static_index(client):
    # Arrange

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_data_and_cache_headers(client):
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json()["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]
    assert response.headers["cache-control"] == "no-store, no-cache, must-revalidate, max-age=0"
    assert response.headers["pragma"] == "no-cache"
    assert response.headers["expires"] == "0"


def test_signup_adds_participant_to_activity(client):
    # Arrange
    email = "new.student@mergington.edu"

    # Act
    response = client.post(f"/activities/Chess%20Club/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activities["Chess Club"]["participants"]


def test_signup_returns_not_found_for_unknown_activity(client):
    # Arrange
    email = "new.student@mergington.edu"

    # Act
    response = client.post(f"/activities/Unknown%20Club/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/Chess%20Club/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}
    assert activities["Chess Club"]["participants"].count(email) == 1


def test_signup_rejects_when_activity_is_full(client):
    # Arrange
    email = "last.spot@mergington.edu"
    activities["Debate Team"]["participants"] = [
        f"student{index}@mergington.edu" for index in range(activities["Debate Team"]["max_participants"])
    ]

    # Act
    response = client.post(f"/activities/Debate%20Team/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Activity is full"}
    assert email not in activities["Debate Team"]["participants"]


def test_unregister_removes_participant_from_activity(client):
    # Arrange
    email = "michael@mergington.edu"

    # Act
    response = client.delete(f"/activities/Chess%20Club/participants?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from Chess Club"}
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_returns_not_found_for_unknown_activity(client):
    # Arrange
    email = "michael@mergington.edu"

    # Act
    response = client.delete(f"/activities/Unknown%20Club/participants?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_returns_not_found_for_missing_participant(client):
    # Arrange
    email = "missing.student@mergington.edu"

    # Act
    response = client.delete(f"/activities/Chess%20Club/participants?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Participant not found for this activity"}
    assert email not in activities["Chess Club"]["participants"]