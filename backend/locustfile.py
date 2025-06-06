from locust import HttpUser, task, between
import json
import random

class APIUser(HttpUser):
    # Base URL for the API
    host = "http://localhost:5000"
    
    # Wait between 1 and 5 seconds between tasks
    wait_time = between(1, 5)
    
    def on_start(self):
        """Initialize user session - login and get token"""
        # Mock authentication for testing
        self.token = "mock-jwt-token"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        # Store created story IDs for subsequent requests
        self.story_ids = []

    @task(3)
    def get_stories(self):
        """Test getting all stories"""
        with self.client.get("/api/stories", headers=self.headers, catch_response=True) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('data') is not None:
                        response.success()
                    else:
                        response.failure("Invalid response format")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"Got status code {response.status_code}")

    @task(2)
    def get_story(self):
        """Test getting a specific story"""
        if not self.story_ids:
            return
        
        story_id = random.choice(self.story_ids)
        with self.client.get(f"/api/stories/{story_id}", headers=self.headers, catch_response=True) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('data') is not None:
                        response.success()
                    else:
                        response.failure("Invalid response format")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"Got status code {response.status_code}")

    @task(1)
    def create_story(self):
        """Test creating a new story"""
        story_data = {
            "title": f"Test Story {random.randint(1, 1000)}",
            "description": "A test story for load testing",
            "genre": random.choice(["mystery", "horror", "thriller"]),
            "difficulty": random.choice(["easy", "medium", "hard"])
        }
        with self.client.post(
            "/api/stories",
            headers=self.headers,
            json=story_data,
            catch_response=True
        ) as response:
            if response.status_code == 201:
                try:
                    data = response.json()
                    if data.get('data') and data['data'].get('id'):
                        self.story_ids.append(data['data']['id'])
                        response.success()
                    else:
                        response.failure("Invalid response format")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"Got status code {response.status_code}")

    @task(2)
    def perform_action(self):
        """Test performing an action in a story"""
        if not self.story_ids:
            return
            
        story_id = random.choice(self.story_ids)
        action_data = {
            "action": random.choice(["investigate", "examine", "talk", "move"]),
            "target": f"target_{random.randint(1, 5)}"
        }
        with self.client.post(
            f"/api/stories/{story_id}/actions",
            headers=self.headers,
            json=action_data,
            catch_response=True
        ) as response:
            if response.status_code in [200, 201]:
                try:
                    data = response.json()
                    if data.get('data') is not None:
                        response.success()
                    else:
                        response.failure("Invalid response format")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"Got status code {response.status_code}")

    @task(2)
    def make_choice(self):
        """Test making a choice in a story"""
        if not self.story_ids:
            return
            
        story_id = random.choice(self.story_ids)
        choice_data = {
            "choice": f"option_{random.randint(1, 3)}"
        }
        with self.client.post(
            f"/api/stories/{story_id}/choices",
            headers=self.headers,
            json=choice_data,
            catch_response=True
        ) as response:
            if response.status_code in [200, 201]:
                try:
                    data = response.json()
                    if data.get('data') is not None:
                        response.success()
                    else:
                        response.failure("Invalid response format")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"Got status code {response.status_code}")

    @task(1)
    def update_story(self):
        """Test updating a story"""
        if not self.story_ids:
            return
            
        story_id = random.choice(self.story_ids)
        update_data = {
            "title": f"Updated Story {random.randint(1, 1000)}",
            "description": "Updated description for load testing"
        }
        with self.client.put(
            f"/api/stories/{story_id}",
            headers=self.headers,
            json=update_data,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('data') is not None:
                        response.success()
                    else:
                        response.failure("Invalid response format")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"Got status code {response.status_code}")

    @task(1)
    def delete_story(self):
        """Test deleting a story"""
        if not self.story_ids:
            return
            
        story_id = random.choice(self.story_ids)
        with self.client.delete(
            f"/api/stories/{story_id}",
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code == 204:
                self.story_ids.remove(story_id)
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")

    @task(2)
    def get_story_progress(self):
        """Test getting story progress"""
        if not self.story_ids:
            return
            
        story_id = random.choice(self.story_ids)
        with self.client.get(
            f"/api/stories/{story_id}/progress",
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('data') is not None:
                        response.success()
                    else:
                        response.failure("Invalid response format")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"Got status code {response.status_code}")

    @task(1)
    def get_story_statistics(self):
        """Test getting story statistics"""
        with self.client.get(
            "/api/stories/statistics",
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('data') is not None:
                        response.success()
                    else:
                        response.failure("Invalid response format")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"Got status code {response.status_code}")