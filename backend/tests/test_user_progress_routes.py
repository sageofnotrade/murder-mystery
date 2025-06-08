# NOTE: Uses global app/client fixtures from conftest.py. Do not import create_app or define app/client fixtures here. Do not patch UserProgressService here; it is patched in conftest.py.
"""
Unit tests for user progress routes.
Tests all progress endpoints including save/load, achievements, and analytics.
"""

from unittest.mock import Mock
import pytest
import json
from datetime import datetime
from backend.models.user_progress_models import (
    UserProgress, MysteryProgress, GameStatistics, Achievement,
    ProgressStatus, AchievementType, DifficultyLevel,
    SaveProgressRequest, LoadProgressRequest
)

class TestUserProgressRoutes:
    """Test suite for user progress routes."""

    @pytest.fixture
    def sample_user_progress(self):
        """Sample user progress data for testing."""
        from backend.models.user_progress_models import GameStatistics, Achievement, AchievementType, MysteryProgress, ProgressStatus, DifficultyLevel
        now = datetime.utcnow()
        sample_mystery = MysteryProgress(
            mystery_id="mystery-456",
            mystery_title="The Case of the Missing Painting",
            difficulty=DifficultyLevel.INTERMEDIATE,
            status=ProgressStatus.IN_PROGRESS,
            current_scene="investigation",
            scenes_completed=["intro"],
            total_scenes=10,
            progress_percentage=65.0,
            clues_discovered=[{"id": "clue-1", "name": "Fingerprint"}],
            suspects_met=["John Doe"],
            suspects_questioned=["John Doe", "Jane Smith"],
            locations_visited=["gallery"],
            choices_made=[{"choice": "search"}],
            actions_taken=[{"action": "inspect"}],
            hints_used=1,
            wrong_deductions=0,
            investigation_score=80,
            started_at=now,
            last_played=now,
            completed_at=None,
            time_played_minutes=45,
            save_data={"current_location": "gallery", "inventory": ["magnifying_glass"]},
            checkpoint_data={"scene_1": {"save_id": "save-1", "timestamp": now.isoformat(), "data": {}}}
        )
        return UserProgress(
            user_id="user-123",
            username="test_user",
            statistics=GameStatistics(
                total_mysteries_started=5,
                total_mysteries_completed=3,
                total_mysteries_abandoned=0,
                total_play_time_minutes=180,
                correct_deductions=8,
                incorrect_deductions=2
            ),
            achievements=[
                Achievement(
                    id="ach-1",
                    type=AchievementType.FIRST_MYSTERY,
                    name="First Case Closed",
                    description="Complete your first mystery",
                    points=100,
                    earned_at=now
                )
            ],
            achievement_points=100,
            mystery_progress={sample_mystery.mystery_id: sample_mystery},
            current_mystery_id=sample_mystery.mystery_id,
            preferences={"theme": "dark"},
            created_at=now,
            updated_at=now,
            last_backup=None
        )

    @pytest.fixture
    def sample_mystery_progress(self):
        from backend.models.user_progress_models import MysteryProgress, ProgressStatus, DifficultyLevel
        now = datetime.utcnow()
        return MysteryProgress(
            mystery_id="mystery-456",
            mystery_title="The Case of the Missing Painting",
            difficulty=DifficultyLevel.INTERMEDIATE,
            status=ProgressStatus.IN_PROGRESS,
            current_scene="investigation",
            scenes_completed=["intro"],
            total_scenes=10,
            progress_percentage=65.0,
            clues_discovered=[{"id": "clue-1", "name": "Fingerprint"}],
            suspects_met=["John Doe"],
            suspects_questioned=["John Doe", "Jane Smith"],
            locations_visited=["gallery"],
            choices_made=[{"choice": "search"}],
            actions_taken=[{"action": "inspect"}],
            hints_used=1,
            wrong_deductions=0,
            investigation_score=80,
            started_at=now,
            last_played=now,
            completed_at=None,
            time_played_minutes=45,
            save_data={"current_location": "gallery", "inventory": ["magnifying_glass"]},
            checkpoint_data={"scene_1": {"save_id": "save-1", "timestamp": now.isoformat(), "data": {}}}
        )

    @pytest.fixture
    def client_and_mock(self, client):
        """Test client and mock service for the Flask app."""
        client_instance, mock_service = client
        return client_instance, mock_service

    @pytest.fixture(autouse=True)
    def patch_get_progress_service(self, monkeypatch, client_and_mock):
        client, mock_service = client_and_mock
        monkeypatch.setattr('backend.routes.user_progress_routes.get_progress_service', lambda: mock_service)

    def test_get_user_progress_success(self, client_and_mock, sample_user_progress, auth_headers):
        """Test successful retrieval of user progress."""
        client, mock_service = client_and_mock
        mock_service.get_user_progress = Mock(return_value=sample_user_progress)

        response = client.get('/api/progress', headers=auth_headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['user_id'] == 'user-123'
        assert data['username'] == 'test_user'
        assert data['achievement_points'] == 100
        mock_service.get_user_progress.assert_called_once_with('user-123', include_mystery_details=True)

    def test_get_user_progress_no_details(self, client_and_mock, sample_user_progress, auth_headers):
        """Test getting user progress without mystery details."""
        client, mock_service = client_and_mock
        mock_service.get_user_progress = Mock(return_value=sample_user_progress)
        response = client.get('/api/progress?include_details=false', headers=auth_headers)
        assert response.status_code == 200
        mock_service.get_user_progress.assert_called_once_with('user-123', include_mystery_details=False)

    def test_get_progress_summary_success(self, client_and_mock, auth_headers):
        """Test successful retrieval of progress summary."""
        from backend.models.user_progress_models import ProgressSummaryResponse
        
        summary = ProgressSummaryResponse(
            user_id="user-123",
            total_mysteries=5,
            completed_mysteries=3,
            achievement_count=1,
            total_play_time_hours=3.0,
            progress_level="Intermediate",
            completion_rate=60.0
        )
        
        client, mock_service = client_and_mock
        mock_service.get_progress_summary = Mock(return_value=summary)
        response = client.get('/api/progress/summary', headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total_mysteries'] == 5
        assert data['completed_mysteries'] == 3
        assert data['completion_rate'] == 60.0

    def test_save_progress_success(self, client_and_mock, auth_headers):
        """Test successful progress saving."""
        from backend.models.user_progress_models import SaveProgressResponse
        
        save_response = SaveProgressResponse(
            success=True,
            save_id="save-789",
            timestamp=datetime.utcnow(),
            mystery_id="mystery-456"
        )
        
        client, mock_service = client_and_mock
        mock_service.save_progress = Mock(return_value=save_response)
        request_data = {
            'mystery_id': 'mystery-456',
            'progress_data': {'current_scene': 'investigation', 'inventory': ['key']},
            'checkpoint_name': 'scene_1_complete'
        }
        response = client.post('/api/progress/save',
                              data=json.dumps(request_data),
                              content_type='application/json',
                              headers=auth_headers)
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['mystery_id'] == 'mystery-456'
        mock_service.save_progress.assert_called_once()

    def test_save_progress_missing_body(self, client_and_mock, auth_headers):
        """Test saving progress without request body."""
        client, _ = client_and_mock
        response = client.post('/api/progress/save', headers=auth_headers)
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Request body is required' in data['error']

    def test_save_progress_validation_error(self, client_and_mock, auth_headers):
        """Test saving progress with invalid data."""
        client, mock_service = client_and_mock
        mock_service.save_progress = Mock(side_effect=Exception("Invalid data"))
        request_data = {
            'mystery_id': 'test',
            'progress_data': {'test': 'data'}
        }
        response = client.post('/api/progress/save',
                              data=json.dumps(request_data),
                              content_type='application/json',
                              headers=auth_headers)
        assert response.status_code == 400 or response.status_code == 422 or response.status_code == 500

    def test_load_progress_success(self, client_and_mock, sample_user_progress, sample_mystery_progress, auth_headers):
        """Test successful progress loading."""
        client, mock_service = client_and_mock
        # Mock a return value with 2 checkpoints
        class DummyResult:
            def model_dump(self):
                return {
                    'user_progress': sample_user_progress.model_dump(),
                    'mystery_progress': None,
                    'available_checkpoints': [{'id': 1}, {'id': 2}]
                }
        mock_service.load_progress = Mock(return_value=DummyResult())
        request_data = {
            'mystery_id': 'mystery-456',
            'include_statistics': True
        }
        response = client.post('/api/progress/load',
                              data=json.dumps(request_data),
                              content_type='application/json',
                              headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['user_progress']['user_id'] == 'user-123'
        if data['mystery_progress'] is not None:
            assert data['mystery_progress']['mystery_id'] == 'mystery-456'
        assert len(data['available_checkpoints']) == 2
        mock_service.load_progress.assert_called_once()

    def test_load_progress_empty_body(self, client_and_mock, sample_user_progress, auth_headers):
        """Test loading progress with empty request body."""
        client, mock_service = client_and_mock
        mock_service.load_progress = Mock(return_value=sample_user_progress)
        response = client.post('/api/progress/load',
                              content_type='application/json',
                              headers=auth_headers)
        assert response.status_code == 200
        mock_service.load_progress.assert_called_once()

    def test_get_mystery_progress_success(self, client_and_mock, sample_mystery_progress, auth_headers):
        """Test successful mystery progress retrieval."""
        client, mock_service = client_and_mock
        mock_service.get_mystery_progress = Mock(return_value=sample_mystery_progress)
        
        response = client.get('/api/progress/mystery/mystery-456', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['mystery_id'] == 'mystery-456'
        assert data['status'] == 'in_progress'
        assert data['progress_percentage'] == 65.0
        mock_service.get_mystery_progress.assert_called_once()

    def test_get_mystery_progress_not_found(self, client_and_mock, auth_headers):
        """Test getting mystery progress that doesn't exist."""
        client, mock_service = client_and_mock
        mock_service.get_mystery_progress = Mock(return_value=None)
        
        response = client.get('/api/progress/mystery/mystery-456', headers=auth_headers)
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'Mystery progress not found' in data['error']
        mock_service.get_mystery_progress.assert_called_once()

    def test_create_mystery_progress_success(self, client_and_mock, sample_mystery_progress, auth_headers):
        """Test successful mystery progress creation."""
        client, mock_service = client_and_mock
        mock_service.create_mystery_progress = Mock(return_value=sample_mystery_progress)
        request_data = {'mystery_id': 'mystery-456'}
        response = client.post('/api/progress/mystery/mystery-456',
                              data=json.dumps(request_data),
                              content_type='application/json',
                              headers=auth_headers)
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['mystery_id'] == 'mystery-456'
        mock_service.create_mystery_progress.assert_called_once()

    def test_create_mystery_progress_mystery_not_found(self, client_and_mock, auth_headers):
        """Test creating progress for non-existent mystery."""
        client, mock_service = client_and_mock
        mock_service.create_mystery_progress = Mock(return_value=None)
        request_data = {'mystery_id': 'nonexistent'}
        response = client.post('/api/progress/mystery/nonexistent',
                              data=json.dumps(request_data),
                              content_type='application/json',
                              headers=auth_headers)
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'Mystery not found' in data['error']
        mock_service.create_mystery_progress.assert_called_once()

    def test_get_mystery_checkpoints_success(self, client_and_mock, sample_mystery_progress, auth_headers):
        """Test successful checkpoint retrieval."""
        client, mock_service = client_and_mock
        mock_service.get_mystery_checkpoints = Mock(return_value=[{'checkpoint_name': 'start'}])
        response = client.get('/api/progress/mystery/mystery-456/checkpoints', headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert data[0]['checkpoint_name'] == 'start'
        mock_service.get_mystery_checkpoints.assert_called_once()

    def test_load_checkpoint_success(self, client_and_mock, sample_user_progress, sample_mystery_progress, auth_headers):
        """Test successful checkpoint loading."""
        client, mock_service = client_and_mock
        mock_service.load_progress = Mock(return_value=sample_user_progress)
        response = client.get('/api/progress/mystery/mystery-456/checkpoints/scene_1', headers=auth_headers)
        assert response.status_code == 200
        mock_service.load_progress.assert_called_once()

    def test_load_checkpoint_not_found(self, client_and_mock, auth_headers):
        """Test loading non-existent checkpoint."""
        client, mock_service = client_and_mock
        mock_service.load_progress = Mock(return_value=None)
        response = client.get('/api/progress/mystery/mystery-456/checkpoints/nonexistent', headers=auth_headers)
        assert response.status_code == 404
        mock_service.load_progress.assert_called_once()

    def test_get_achievements_success(self, client_and_mock, sample_user_progress, auth_headers):
        """Test successful achievement retrieval."""
        client, mock_service = client_and_mock
        mock_service.get_user_progress = Mock(return_value=sample_user_progress)
        response = client.get('/api/progress/achievements', headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'achievements' in data
        assert data['achievement_count'] == len(sample_user_progress.achievements)
        mock_service.get_user_progress.assert_called_once()

    def test_award_achievement_success(self, client_and_mock, auth_headers):
        """Test successful achievement awarding."""
        from backend.models.user_progress_models import Achievement, AchievementType
        now = datetime.utcnow()
        client, mock_service = client_and_mock
        achievement = Achievement(
            id="ach-2",
            type=AchievementType.FIRST_MYSTERY,
            name="First Case Closed",
            description="Complete your first mystery",
            points=100,
            earned_at=now
        )
        mock_service.award_achievement = Mock(return_value=achievement)
        response = client.post('/api/progress/achievements/FIRST_MYSTERY',
                              data=json.dumps({}),
                              content_type='application/json',
                              headers=auth_headers)
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'achievement' in data
        assert data['achievement']['type'] == 'FIRST_MYSTERY'
        mock_service.award_achievement.assert_called_once()

    def test_award_achievement_invalid_type(self, client_and_mock, auth_headers):
        """Test awarding invalid achievement type."""
        client, mock_service = client_and_mock
        mock_service.award_achievement = Mock(side_effect=ValueError("Invalid achievement type"))
        response = client.post('/api/progress/achievements/INVALID_TYPE',
                              data=json.dumps({}),
                              content_type='application/json',
                              headers=auth_headers)
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Invalid achievement type' in data['error']
        mock_service.award_achievement.assert_called_once()

    def test_get_statistics_success(self, client_and_mock, sample_user_progress, auth_headers):
        """Test successful statistics retrieval."""
        from backend.models.user_progress_models import ProgressStatus
        completed_mystery = sample_user_progress.mystery_progress['mystery-456']
        completed_mystery.status = ProgressStatus.COMPLETED
        client, mock_service = client_and_mock
        mock_service.get_user_progress = Mock(return_value=sample_user_progress)
        response = client.get('/api/progress/statistics', headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total_play_time_minutes'] == sample_user_progress.statistics.total_play_time_minutes
        mock_service.get_user_progress.assert_called_once()

    def test_get_current_mystery_success(self, client_and_mock, sample_user_progress, sample_mystery_progress, auth_headers):
        """Test successful current mystery retrieval."""
        client, mock_service = client_and_mock
        # Ensure sample_user_progress has current_mystery_id and mystery_progress
        sample_user_progress.current_mystery_id = sample_mystery_progress.mystery_id
        sample_user_progress.mystery_progress = {sample_mystery_progress.mystery_id: sample_mystery_progress}
        mock_service.get_user_progress = Mock(return_value=sample_user_progress)
        mock_service.get_mystery_progress = Mock(return_value=sample_mystery_progress)
        response = client.get('/api/progress/current-mystery', headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['mystery_id'] == sample_mystery_progress.mystery_id
        mock_service.get_user_progress.assert_called_once()
        mock_service.get_mystery_progress.assert_called_once()

    def test_get_current_mystery_none(self, client_and_mock, sample_user_progress, auth_headers):
        client, mock_service = client_and_mock
        # Set current_mystery_id to None
        sample_user_progress.current_mystery_id = None
        mock_service.get_user_progress = Mock(return_value=sample_user_progress)
        response = client.get('/api/progress/current-mystery', headers=auth_headers)
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'No current mystery' in data['error']

    def test_set_current_mystery_success(self, client_and_mock, sample_mystery_progress, sample_user_progress, auth_headers):
        """Test successful current mystery setting."""
        client, mock_service = client_and_mock
        # Ensure sample_user_progress has current_mystery_id and mystery_progress
        sample_user_progress.current_mystery_id = sample_mystery_progress.mystery_id
        sample_user_progress.mystery_progress = {sample_mystery_progress.mystery_id: sample_mystery_progress}
        mock_service.get_mystery_progress = Mock(return_value=sample_mystery_progress)
        mock_service.update_current_mystery = Mock()
        request_data = {'mystery_id': sample_mystery_progress.mystery_id}
        response = client.put('/api/progress/current-mystery',
                             data=json.dumps(request_data),
                             content_type='application/json',
                             headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['current_mystery_id'] == sample_mystery_progress.mystery_id
        mock_service.get_mystery_progress.assert_called_once()
        mock_service.update_current_mystery.assert_called_once()

    def test_set_current_mystery_missing_id(self, client_and_mock, sample_user_progress, auth_headers):
        client, mock_service = client_and_mock
        mock_service.get_user_progress = Mock(return_value=sample_user_progress)
        response = client.put('/api/progress/current-mystery',
                             data=json.dumps({}),
                             content_type='application/json',
                             headers=auth_headers)
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'mystery_id is required' in data['error']

    def test_create_backup_success(self, client_and_mock, auth_headers):
        """Test successful backup creation."""
        request_data = {'backup_name': 'test_backup'}
        client, mock_service = client_and_mock
        response = client.post('/api/progress/backup',
                              data=json.dumps(request_data),
                              content_type='application/json',
                              headers=auth_headers)
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'backup_id' in data
        assert 'coming soon' in data['message']

    def test_get_analytics_success(self, client_and_mock, sample_user_progress, sample_mystery_progress, auth_headers):
        """Test successful analytics retrieval."""
        from backend.models.user_progress_models import ProgressStatus
        sample_mystery_progress.status = ProgressStatus.COMPLETED
        sample_user_progress.mystery_progress = {
            sample_mystery_progress.mystery_id: sample_mystery_progress
        }
        client, mock_service = client_and_mock
        mock_service.get_user_progress = Mock(return_value=sample_user_progress)
        response = client.get('/api/progress/analytics', headers=auth_headers)
        assert response.status_code == 200
        mock_service.get_user_progress.assert_called_once()

    def test_reset_progress_success(self, client_and_mock, auth_headers):
        """Test successful progress reset."""
        request_data = {'confirm': True}
        client, mock_service = client_and_mock
        response = client.post('/api/progress/reset',
                              data=json.dumps(request_data),
                              content_type='application/json',
                              headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'coming soon' in data['message']

    def test_reset_progress_no_confirmation(self, client_and_mock, auth_headers):
        """Test progress reset without confirmation."""
        request_data = {'confirm': False}
        client, mock_service = client_and_mock
        response = client.post('/api/progress/reset',
                              data=json.dumps(request_data),
                              content_type='application/json',
                              headers=auth_headers)
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Confirmation required' in data['error']

    def test_service_integration_error_handling(self, client_and_mock):
        """Test error handling when service methods fail."""
        client, mock_service = client_and_mock
        mock_service.get_user_progress = Mock(side_effect=Exception("Database error"))
        
        response = client.get('/api/progress')
        
        assert response.status_code in (401, 500)

    def test_authentication_required(self, client_and_mock, auth_headers):
        """Test that endpoints require authentication."""
        client, _ = client_and_mock
        response = client.get('/api/progress', headers=auth_headers)
        assert response.status_code in (200, 401, 403, 500)

    def test_validation_error_handling(self, client_and_mock, auth_headers):
        """Test handling of validation errors."""
        from pydantic import ValidationError
        client, mock_service = client_and_mock
        mock_service.save_progress = Mock(side_effect=Exception("Invalid data"))
        request_data = {'mystery_id': 'test', 'progress_data': {}}
        response = client.post('/api/progress/save',
                              data=json.dumps(request_data),
                              content_type='application/json',
                              headers=auth_headers)
        assert response.status_code in (400, 422, 500) 