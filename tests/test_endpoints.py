"""
Tests for FastAPI endpoints using the AAA (Arrange-Act-Assert) pattern.

Each test is organized into three clear sections:
- Arrange: Set up test data and conditions
- Act: Execute the code being tested
- Assert: Verify the results
"""

import pytest


class TestRootEndpoint:
    """Tests for the GET / endpoint."""

    def test_root_redirect(self, client):
        """Test that root endpoint redirects to /static/index.html"""
        # Arrange
        expected_redirect_path = "/static/index.html"

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == expected_redirect_path


class TestGetActivitiesEndpoint:
    """Tests for the GET /activities endpoint."""

    def test_get_activities_success(self, client):
        """Test that get_activities returns all activities with correct structure"""
        # Arrange
        expected_activity_count = 9
        expected_activity_keys = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == expected_activity_count
        
        # Verify each activity has the correct structure
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_name, str)
            assert activity_data.keys() == expected_activity_keys
            assert isinstance(activity_data["participants"], list)
            assert isinstance(activity_data["max_participants"], int)

    def test_get_activities_contains_chess_club(self, client):
        """Test that Chess Club is in activities with correct initial participants"""
        # Arrange
        expected_participants = ["michael@mergington.edu", "daniel@mergington.edu"]

        # Act
        response = client.get("/activities")

        # Assert
        activities = response.json()
        assert "Chess Club" in activities
        assert activities["Chess Club"]["participants"] == expected_participants


class TestSignupEndpoint:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_success(self, client):
        """Test successful signup for an activity"""
        # Arrange
        email = "newstudent@mergington.edu"
        activity = "Chess Club"

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        assert email in response.json()["message"]
        assert activity in response.json()["message"]

    def test_signup_student_appears_in_activity(self, client):
        """Test that signed-up student appears in activity participants list"""
        # Arrange
        email = "newstudent@mergington.edu"
        activity = "Programming Class"

        # Act
        client.post(f"/activities/{activity}/signup?email={email}")
        response = client.get("/activities")

        # Assert
        activities = response.json()
        assert email in activities[activity]["participants"]

    def test_signup_activity_not_found(self, client):
        """Test signup returns 404 when activity does not exist"""
        # Arrange
        email = "student@mergington.edu"
        nonexistent_activity = "Nonexistent Club"

        # Act
        response = client.post(f"/activities/{nonexistent_activity}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_duplicate_email(self, client):
        """Test signup returns 400 when student already signed up"""
        # Arrange
        email = "michael@mergington.edu"  # Already in Chess Club
        activity = "Chess Club"

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_same_student_different_activities(self, client):
        """Test that a student can sign up for multiple different activities"""
        # Arrange
        email = "newstudent@mergington.edu"
        activity1 = "Chess Club"
        activity2 = "Programming Class"

        # Act
        response1 = client.post(f"/activities/{activity1}/signup?email={email}")
        response2 = client.post(f"/activities/{activity2}/signup?email={email}")

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify student is in both activities
        response = client.get("/activities")
        activities = response.json()
        assert email in activities[activity1]["participants"]
        assert email in activities[activity2]["participants"]


class TestUnregisterEndpoint:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_success(self, client):
        """Test successful unregistration from an activity"""
        # Arrange
        email = "michael@mergington.edu"  # Already in Chess Club
        activity = "Chess Club"
        initial_count = len(client.get("/activities").json()[activity]["participants"])

        # Act
        response = client.delete(f"/activities/{activity}/unregister?email={email}")

        # Assert
        assert response.status_code == 200
        assert email in response.json()["message"]
        assert activity in response.json()["message"]

    def test_unregister_student_removed_from_activity(self, client):
        """Test that unregistered student no longer appears in activity participants"""
        # Arrange
        email = "michael@mergington.edu"
        activity = "Chess Club"

        # Act
        client.delete(f"/activities/{activity}/unregister?email={email}")
        response = client.get("/activities")

        # Assert
        activities = response.json()
        assert email not in activities[activity]["participants"]

    def test_unregister_activity_not_found(self, client):
        """Test unregister returns 404 when activity does not exist"""
        # Arrange
        email = "student@mergington.edu"
        nonexistent_activity = "Nonexistent Club"

        # Act
        response = client.delete(f"/activities/{nonexistent_activity}/unregister?email={email}")

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_student_not_signed_up(self, client):
        """Test unregister returns 400 when student is not signed up"""
        # Arrange
        email = "notstudent@mergington.edu"
        activity = "Chess Club"

        # Act
        response = client.delete(f"/activities/{activity}/unregister?email={email}")

        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_then_signup_again(self, client):
        """Test that a student can re-signup after unregistering"""
        # Arrange
        email = "testuser@mergington.edu"
        activity = "Tennis Club"

        # Act
        # First signup
        response1 = client.post(f"/activities/{activity}/signup?email={email}")
        # Then unregister
        response2 = client.delete(f"/activities/{activity}/unregister?email={email}")
        # Then signup again
        response3 = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response3.status_code == 200
        
        # Verify student is in activity after final signup
        response = client.get("/activities")
        activities = response.json()
        assert email in activities[activity]["participants"]


class TestIntegrationScenarios:
    """Integration tests combining multiple endpoints."""

    def test_signup_and_verify_activity_update(self, client):
        """
        Integration test: Sign up a student and verify the activity list reflects
        the change.
        """
        # Arrange
        email = "integration@test.edu"
        activity = "Debate Club"
        initial_response = client.get("/activities")
        initial_participants = initial_response.json()[activity]["participants"].copy()

        # Act
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        final_response = client.get("/activities")

        # Assert
        assert signup_response.status_code == 200
        final_participants = final_response.json()[activity]["participants"]
        assert email in final_participants
        assert len(final_participants) == len(initial_participants) + 1

    def test_multiple_signups_and_unregister(self, client):
        """
        Integration test: Sign up multiple students and unregister one,
        verifying participant counts.
        """
        # Arrange
        activity = "Science Olympiad"
        students = ["student1@test.edu", "student2@test.edu", "student3@test.edu"]
        
        # Act
        for student in students:
            client.post(f"/activities/{activity}/signup?email={student}")
        
        # Unregister the second student
        client.delete(f"/activities/{activity}/unregister?email={students[1]}")
        
        # Assert
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]
        
        assert students[0] in participants
        assert students[1] not in participants
        assert students[2] in participants
