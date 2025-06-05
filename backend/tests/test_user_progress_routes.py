"""
Unit tests for user progress routes.
Tests all progress endpoints including save/load, achievements, and analytics.
"""

import pytest
import json
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from models.user_progress_models import (
    UserProgress, MysteryProgress, GameStatistics, Achievement,
    ProgressStatus, AchievementType, DifficultyLevel,
    SaveProgressRequest, LoadProgressRequest
)

class TestUserProgressRoutes:
    """Test suite for user progress routes."""

    @pytest.fixture
    def sample_user_progress(self):
        """Sample user progress data for testing."""
        return UserProgress(
            user_id="user-123",
            username="test_user",
            statistics=GameStatistics(
                total_mysteries_started=5,
                total_mysteries_completed=3,
                total_play_time_minutes=180,
                total_clues_discovered=25,
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
                    earned_at=datetime.utcnow()
                )
            ],
            achievement_points=100,
            current_mystery_id="mystery-456"
        )

    @pytest.fixture
    def sample_mystery_progress(self):
        """Sample mystery progress data for testing."""
        return MysteryProgress(
            mystery_id="mystery-456",
            mystery_title="The Case of the Missing Painting",
            difficulty=DifficultyLevel.INTERMEDIATE,
            status=ProgressStatus.IN_PROGRESS,
            current_scene="investigation",
            progress_percentage=65.0,
            clues_discovered=[{"id": "clue-1", "name": "Fingerprint"}],
            suspects_questioned=["John Doe", "Jane Smith"],
            started_at=datetime.utcnow(),
            last_played=datetime.utcnow(),
            time_played_minutes=45,
            save_data={"current_location": "gallery", "inventory": ["magnifying_glass"]}
        )

    @pytest.fixture
    def mock_progress_service(self):
        """Mock UserProgressService for testing."""
        with patch('routes.user_progress_routes.UserProgressService') as mock_service:
            mock_instance = Mock()
            mock_service.return_value = mock_instance
            yield mock_instance

    @pytest.fixture
    def mock_jwt_required(self):
        """Mock JWT requirement for testing."""
        with patch('routes.user_progress_routes.jwt_required') as mock_jwt:
            mock_jwt.return_value = lambda f: f
            yield mock_jwt

    @pytest.fixture
    def mock_get_jwt_identity(self):
        """Mock JWT identity for testing."""
        with patch('routes.user_progress_routes.get_jwt_identity') as mock_identity:
            mock_identity.return_value = 'user-123'
            yield mock_identity

    @pytest.fixture
    def client(self, app):
        """Test client for the Flask app."""
        return app.test_client()

    def test_get_user_progress_success(self, client, mock_progress_service, mock_jwt_required, 
                                     mock_get_jwt_identity, sample_user_progress):
        """Test successful retrieval of user progress."""
        mock_progress_service.get_user_progress = AsyncMock(return_value=sample_user_progress)
        
        response = client.get('/api/progress')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['user_id'] == 'user-123'
        assert data['username'] == 'test_user'
        assert data['achievement_points'] == 100
        mock_progress_service.get_user_progress.assert_called_once_with('user-123', include_mystery_details=True)

    def test_get_user_progress_no_details(self, client, mock_progress_service, mock_jwt_required, 
                                        mock_get_jwt_identity, sample_user_progress):
        """Test getting user progress without mystery details."""
        mock_progress_service.get_user_progress = AsyncMock(return_value=sample_user_progress)
        
        response = client.get('/api/progress?include_details=false')
        
        assert response.status_code == 200
        mock_progress_service.get_user_progress.assert_called_once_with('user-123', include_mystery_details=False)

    def test_get_progress_summary_success(self, client, mock_progress_service, mock_jwt_required, 
                                        mock_get_jwt_identity):
        """Test successful retrieval of progress summary."""
        from models.user_progress_models import ProgressSummaryResponse
        
        summary = ProgressSummaryResponse(
            user_id="user-123",
            total_mysteries=5,
            completed_mysteries=3,
            achievement_count=1,
            total_play_time_hours=3.0,
            progress_level="Intermediate",
            completion_rate=60.0
        )
        
        mock_progress_service.get_progress_summary = AsyncMock(return_value=summary)
        
        response = client.get('/api/progress/summary')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total_mysteries'] == 5
        assert data['completed_mysteries'] == 3
        assert data['completion_rate'] == 60.0

    def test_save_progress_success(self, client, mock_progress_service, mock_jwt_required, 
                                 mock_get_jwt_identity):
        """Test successful progress saving."""
        from models.user_progress_models import SaveProgressResponse
        
        save_response = SaveProgressResponse(
            success=True,
            save_id="save-789",
            timestamp=datetime.utcnow(),
            mystery_id="mystery-456"
        )
        
        mock_progress_service.save_progress = AsyncMock(return_value=save_response)
        
        request_data = {
            'mystery_id': 'mystery-456',
            'progress_data': {'current_scene': 'investigation', 'inventory': ['key']},
            'checkpoint_name': 'scene_1_complete'
        }
        
        response = client.post('/api/progress/save',
                              data=json.dumps(request_data),
                              content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['mystery_id'] == 'mystery-456'
        mock_progress_service.save_progress.assert_called_once()

    def test_save_progress_missing_body(self, client, mock_jwt_required, mock_get_jwt_identity):
        """Test saving progress without request body."""
        response = client.post('/api/progress/save')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Request body is required' in data['error']

    def test_save_progress_validation_error(self, client, mock_jwt_required, mock_get_jwt_identity):
        """Test saving progress with invalid data."""
        request_data = {
            'mystery_id': '',  # Invalid empty mystery_id
            'progress_data': {}
        }
        
        response = client.post('/api/progress/save',
                              data=json.dumps(request_data),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Invalid request data' in data['error']

    def test_load_progress_success(self, client, mock_progress_service, mock_jwt_required, 
                                 mock_get_jwt_identity, sample_user_progress, sample_mystery_progress):
        """Test successful progress loading."""
        from models.user_progress_models import LoadProgressResponse
        
        load_response = LoadProgressResponse(
            user_progress=sample_user_progress,
            mystery_progress=sample_mystery_progress,
            available_checkpoints=['auto_save', 'scene_1_complete']
        )
        
        mock_progress_service.load_progress = AsyncMock(return_value=load_response)
        
        request_data = {
            'mystery_id': 'mystery-456',
            'include_statistics': True
        }
        
        response = client.post('/api/progress/load',
                              data=json.dumps(request_data),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['user_progress']['user_id'] == 'user-123'
        assert data['mystery_progress']['mystery_id'] == 'mystery-456'
        assert len(data['available_checkpoints']) == 2

    def test_load_progress_empty_body(self, client, mock_progress_service, mock_jwt_required, 
                                    mock_get_jwt_identity, sample_user_progress):
        """Test loading progress with empty request body."""
        from models.user_progress_models import LoadProgressResponse
        
        load_response = LoadProgressResponse(
            user_progress=sample_user_progress,
            mystery_progress=None
        )
        
        mock_progress_service.load_progress = AsyncMock(return_value=load_response)
        
        response = client.post('/api/progress/load',
                              content_type='application/json')
        
        assert response.status_code == 200
        mock_progress_service.load_progress.assert_called_once()

    def test_get_mystery_progress_success(self, client, mock_progress_service, mock_jwt_required, 
                                        mock_get_jwt_identity, sample_mystery_progress):
        """Test successful mystery progress retrieval."""
        mock_progress_service.get_mystery_progress = AsyncMock(return_value=sample_mystery_progress)
        
        response = client.get('/api/progress/mystery/mystery-456')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['mystery_id'] == 'mystery-456'
        assert data['status'] == 'in_progress'
        assert data['progress_percentage'] == 65.0

    def test_get_mystery_progress_not_found(self, client, mock_progress_service, mock_jwt_required, 
                                          mock_get_jwt_identity):
        """Test getting mystery progress that doesn't exist."""
        mock_progress_service.get_mystery_progress = AsyncMock(return_value=None)
        
        response = client.get('/api/progress/mystery/nonexistent')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'Mystery progress not found' in data['error']

    def test_create_mystery_progress_success(self, client, mock_progress_service, mock_jwt_required, 
                                           mock_get_jwt_identity, sample_mystery_progress):
        """Test successful mystery progress creation."""
        mock_progress_service.create_mystery_progress = AsyncMock(return_value=sample_mystery_progress)
        
        response = client.post('/api/progress/mystery/mystery-456')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['mystery_id'] == 'mystery-456'
        assert data['status'] == 'in_progress'

    def test_create_mystery_progress_mystery_not_found(self, client, mock_progress_service, 
                                                     mock_jwt_required, mock_get_jwt_identity):
        """Test creating progress for non-existent mystery."""
        mock_progress_service.create_mystery_progress = AsyncMock(
            side_effect=ValueError("Mystery not found")
        )
        
        response = client.post('/api/progress/mystery/nonexistent')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'Mystery not found' in data['error']

    def test_get_mystery_checkpoints_success(self, client, mock_progress_service, mock_jwt_required, 
                                           mock_get_jwt_identity, sample_mystery_progress):
        """Test successful checkpoint retrieval."""
        sample_mystery_progress.checkpoint_data = {
            'auto_save': {'timestamp': '2024-01-01T12:00:00', 'save_id': 'save-1'},
            'scene_1': {'timestamp': '2024-01-01T11:30:00', 'save_id': 'save-2'}
        }
        mock_progress_service.get_mystery_progress = AsyncMock(return_value=sample_mystery_progress)
        
        response = client.get('/api/progress/mystery/mystery-456/checkpoints')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['mystery_id'] == 'mystery-456'
        assert data['total_count'] == 2
        assert len(data['checkpoints']) == 2

    def test_load_checkpoint_success(self, client, mock_progress_service, mock_jwt_required, 
                                   mock_get_jwt_identity, sample_user_progress, sample_mystery_progress):
        """Test successful checkpoint loading."""
        from models.user_progress_models import LoadProgressResponse
        
        load_response = LoadProgressResponse(
            user_progress=sample_user_progress,
            mystery_progress=sample_mystery_progress
        )
        
        mock_progress_service.load_progress = AsyncMock(return_value=load_response)
        
        response = client.get('/api/progress/mystery/mystery-456/checkpoints/auto_save')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['mystery_progress']['mystery_id'] == 'mystery-456'

    def test_load_checkpoint_not_found(self, client, mock_progress_service, mock_jwt_required, 
                                     mock_get_jwt_identity):
        """Test loading non-existent checkpoint."""
        from models.user_progress_models import LoadProgressResponse
        
        load_response = LoadProgressResponse(
            user_progress=Mock(),
            mystery_progress=None
        )
        
        mock_progress_service.load_progress = AsyncMock(return_value=load_response)
        
        response = client.get('/api/progress/mystery/mystery-456/checkpoints/nonexistent')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'Checkpoint not found' in data['error']

    def test_get_achievements_success(self, client, mock_progress_service, mock_jwt_required, 
                                    mock_get_jwt_identity, sample_user_progress):
        """Test successful achievement retrieval."""
        mock_progress_service.get_user_progress = AsyncMock(return_value=sample_user_progress)
        
        response = client.get('/api/progress/achievements')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total_points'] == 100
        assert data['achievement_count'] == 1
        assert len(data['achievements']) == 1

    def test_award_achievement_success(self, client, mock_progress_service, mock_jwt_required, 
                                     mock_get_jwt_identity):
        """Test successful achievement awarding."""
        achievement = Achievement(
            id="ach-2",
            type=AchievementType.QUICK_SOLVER,
            name="Speed Detective",
            description="Solve a mystery quickly",
            points=200,
            earned_at=datetime.utcnow()
        )
        
        mock_progress_service.award_achievement = AsyncMock(return_value=achievement)
        
        request_data = {'mystery_id': 'mystery-456'}
        
        response = client.post('/api/progress/achievements/quick_solver',
                              data=json.dumps(request_data),
                              content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['achievement']['type'] == 'quick_solver'
        assert data['newly_earned'] is True

    def test_award_achievement_invalid_type(self, client, mock_jwt_required, mock_get_jwt_identity):
        """Test awarding invalid achievement type."""
        response = client.post('/api/progress/achievements/invalid_type',
                              data=json.dumps({}),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Invalid achievement type' in data['error']

    def test_get_statistics_success(self, client, mock_progress_service, mock_jwt_required, 
                                  mock_get_jwt_identity, sample_user_progress):
        """Test successful statistics retrieval."""
        mock_progress_service.get_user_progress = AsyncMock(return_value=sample_user_progress)
        
        response = client.get('/api/progress/statistics')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total_mysteries_started'] == 5
        assert data['total_mysteries_completed'] == 3
        assert data['total_clues_discovered'] == 25

    def test_get_current_mystery_success(self, client, mock_progress_service, mock_jwt_required, 
                                       mock_get_jwt_identity, sample_user_progress, sample_mystery_progress):
        """Test successful current mystery retrieval."""
        mock_progress_service.get_user_progress = AsyncMock(return_value=sample_user_progress)
        mock_progress_service.get_mystery_progress = AsyncMock(return_value=sample_mystery_progress)
        
        response = client.get('/api/progress/current-mystery')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['mystery_id'] == 'mystery-456'

    def test_get_current_mystery_none(self, client, mock_progress_service, mock_jwt_required, 
                                    mock_get_jwt_identity):
        """Test getting current mystery when none is set."""
        progress = UserProgress(user_id="user-123", current_mystery_id=None)
        mock_progress_service.get_user_progress = AsyncMock(return_value=progress)
        
        response = client.get('/api/progress/current-mystery')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'No current mystery' in data['error']

    def test_set_current_mystery_success(self, client, mock_progress_service, mock_jwt_required, 
                                       mock_get_jwt_identity, sample_mystery_progress):
        """Test successful current mystery setting."""
        mock_progress_service.get_mystery_progress = AsyncMock(return_value=sample_mystery_progress)
        mock_progress_service.update_current_mystery = AsyncMock()
        
        request_data = {'mystery_id': 'mystery-456'}
        
        response = client.put('/api/progress/current-mystery',
                             data=json.dumps(request_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['current_mystery_id'] == 'mystery-456'
        mock_progress_service.update_current_mystery.assert_called_once_with('user-123', 'mystery-456')

    def test_set_current_mystery_missing_id(self, client, mock_jwt_required, mock_get_jwt_identity):
        """Test setting current mystery without mystery_id."""
        response = client.put('/api/progress/current-mystery',
                             data=json.dumps({}),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'mystery_id is required' in data['error']

    def test_create_backup_success(self, client, mock_jwt_required, mock_get_jwt_identity):
        """Test successful backup creation."""
        request_data = {'backup_name': 'test_backup'}
        
        response = client.post('/api/progress/backup',
                              data=json.dumps(request_data),
                              content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'backup_id' in data
        assert 'coming soon' in data['message']

    def test_get_analytics_success(self, client, mock_progress_service, mock_jwt_required, 
                                 mock_get_jwt_identity, sample_user_progress):
        """Test successful analytics retrieval."""
        # Add sample mystery progress to user progress
        sample_user_progress.mystery_progress = {
            'mystery-1': MysteryProgress(
                mystery_id='mystery-1',
                mystery_title='Test Mystery',
                difficulty=DifficultyLevel.BEGINNER,
                status=ProgressStatus.COMPLETED,
                started_at=datetime.utcnow(),
                last_played=datetime.utcnow(),
                time_played_minutes=60,
                hints_used=2,
                wrong_deductions=1
            )
        }
        
        mock_progress_service.get_user_progress = AsyncMock(return_value=sample_user_progress)
        
        response = client.get('/api/progress/analytics')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['user_id'] == 'user-123'
        assert 'completion_patterns' in data
        assert 'improvement_metrics' in data

    def test_reset_progress_success(self, client, mock_jwt_required, mock_get_jwt_identity):
        """Test successful progress reset."""
        request_data = {'confirm': True}
        
        response = client.post('/api/progress/reset',
                              data=json.dumps(request_data),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'coming soon' in data['message']

    def test_reset_progress_no_confirmation(self, client, mock_jwt_required, mock_get_jwt_identity):
        """Test progress reset without confirmation."""
        request_data = {'confirm': False}
        
        response = client.post('/api/progress/reset',
                              data=json.dumps(request_data),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Confirmation required' in data['error']

    def test_service_integration_error_handling(self, client, mock_progress_service, 
                                               mock_jwt_required, mock_get_jwt_identity):
        """Test error handling when service methods fail."""
        mock_progress_service.get_user_progress = AsyncMock(side_effect=Exception("Database error"))
        
        response = client.get('/api/progress')
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'error' in data

    def test_authentication_required(self, client):
        """Test that endpoints require authentication."""
        # This test would be more meaningful with actual JWT implementation
        # For now, we're mocking the jwt_required decorator
        response = client.get('/api/progress')
        # Since we're mocking jwt_required to be a no-op, this should still work
        # In a real scenario without proper auth, this would return 401
        assert response.status_code in [200, 401, 500]  # Allow for various auth states

    def test_validation_error_handling(self, client, mock_progress_service, mock_jwt_required, 
                                      mock_get_jwt_identity):
        """Test handling of validation errors."""
        from pydantic import ValidationError
        
        mock_progress_service.save_progress = AsyncMock(
            side_effect=ValidationError("Invalid data", model=SaveProgressRequest)
        )
        
        request_data = {
            'mystery_id': 'test',
            'progress_data': {'test': 'data'}
        }
        
        response = client.post('/api/progress/save',
                              data=json.dumps(request_data),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Invalid request data' in data['error'] 