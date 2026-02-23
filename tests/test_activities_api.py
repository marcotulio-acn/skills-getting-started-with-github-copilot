"""
Integration tests for the Mergington High School Activities API.

Using the AAA (Arrange-Act-Assert) pattern for clarity and maintainability.
"""

import pytest


class TestGetActivities:
    """Tests for the GET /activities endpoint."""

    def test_get_all_activities_success(self, client):
        """
        Arrange: API client is ready
        Act: Make GET request to /activities
        Assert: Response returns 200 with all activities
        """
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) > 0
        # Verify standard activity exists
        assert "Chess Club" in activities

    def test_activity_structure(self, client):
        """
        Arrange: API client is ready
        Act: Fetch activities from the API
        Assert: Each activity has the required fields
        """
        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert - check first activity structure
        first_activity = activities[list(activities.keys())[0]]
        assert "description" in first_activity
        assert "schedule" in first_activity
        assert "max_participants" in first_activity
        assert "participants" in first_activity
        assert isinstance(first_activity["participants"], list)

    def test_activities_have_participants(self, client):
        """
        Arrange: API client is ready
        Act: Fetch activities from the API
        Assert: Activities have participants (some have at least one)
        """
        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert - at least one activity should have participants
        has_participants = any(
            len(activity["participants"]) > 0
            for activity in activities.values()
        )
        assert has_participants


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_success(self, client, existing_activity, sample_email):
        """
        Arrange: API client and test data are ready
        Act: Submit signup request for a valid activity
        Assert: Response returns 200 with success message
        """
        # Act
        response = client.post(
            f"/activities/{existing_activity}/signup?email={sample_email}"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "signed up" in data["message"].lower()

    def test_signup_adds_participant_to_activity(self, client, existing_activity):
        """
        Arrange: API client and test data are ready
        Act: Sign up a new user and fetch activities to verify
        Assert: The new email appears in the activity's participants list
        """
        # Arrange
        test_email = "new.participant@mergington.edu"

        # Act
        signup_response = client.post(
            f"/activities/{existing_activity}/signup?email={test_email}"
        )
        activities_response = client.get("/activities")

        # Assert
        assert signup_response.status_code == 200
        activities = activities_response.json()
        participants = activities[existing_activity]["participants"]
        assert test_email in participants

    def test_signup_duplicate_email_rejected(self, client, existing_activity):
        """
        Arrange: API client and test data are ready
        Act: Sign up the same email twice for the same activity
        Assert: Second signup returns 400 error
        """
        # Arrange
        test_email = "duplicate.test@mergington.edu"

        # Act - First signup
        first_response = client.post(
            f"/activities/{existing_activity}/signup?email={test_email}"
        )
        # Act - Second signup with same email
        second_response = client.post(
            f"/activities/{existing_activity}/signup?email={test_email}"
        )

        # Assert
        assert first_response.status_code == 200
        assert second_response.status_code == 400
        assert "already signed up" in second_response.json()["detail"].lower()

    def test_signup_nonexistent_activity_404(self, client, nonexistent_activity, sample_email):
        """
        Arrange: API client and non-existent activity name
        Act: Attempt to sign up for an activity that doesn't exist
        Assert: Response returns 404 not found
        """
        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/signup?email={sample_email}"
        )

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_signup_with_various_email_formats(self, client, existing_activity):
        """
        Arrange: API client and various email formats
        Act: Sign up users with different valid email formats
        Assert: All signup requests succeed
        """
        # Arrange
        test_emails = [
            "user1@mergington.edu",
            "user.name@mergington.edu",
            "user+tag@mergington.edu",
        ]

        # Act & Assert
        for email in test_emails:
            response = client.post(
                f"/activities/{existing_activity}/signup?email={email}"
            )
            assert response.status_code == 200


class TestRootEndpoint:
    """Tests for the GET / endpoint."""

    def test_root_redirect(self, client):
        """
        Arrange: API client is ready
        Act: Make GET request to root path
        Assert: Request is redirected to static index page
        """
        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307  # Temporary redirect
        assert "/static/index.html" in response.headers["location"]

    def test_root_follows_redirect(self, client):
        """
        Arrange: API client is ready
        Act: Make GET request to root path and follow redirects
        Assert: Final response is successful
        """
        # Act
        response = client.get("/", follow_redirects=True)

        # Assert
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]


class TestApiErrorHandling:
    """Tests for error handling and edge cases."""

    def test_missing_email_parameter_in_signup(self, client, existing_activity):
        """
        Arrange: Activity exists but email parameter is missing
        Act: Attempt to sign up without providing email
        Assert: Request fails appropriately
        """
        # Act
        response = client.post(
            f"/activities/{existing_activity}/signup"
        )

        # Assert - Should fail due to missing email parameter
        assert response.status_code in [422, 400]

    def test_special_characters_in_activity_name(self, client, sample_email):
        """
        Arrange: API client and sample email
        Act: Attempt to sign up for activity with special characters in name
        Assert: Request returns 404 not found
        """
        # Act
        response = client.post(
            f"/activities/Activity%20With%20Special%20%26%20Chars/signup?email={sample_email}"
        )

        # Assert
        assert response.status_code == 404

    def test_response_json_format(self, client):
        """
        Arrange: API client is ready
        Act: Make request to activities endpoint
        Assert: Response is valid JSON
        """
        # Act
        response = client.get("/activities")

        # Assert
        assert response.headers["content-type"] == "application/json"
        activities = response.json()
        assert isinstance(activities, dict)
