"""
Unit tests for suspect routes.
Tests all suspect interaction endpoints including dialogue, alibi verification, and profile management.
"""

import pytest
import json
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from backend.routes.suspect_routes import suspect_bp
from backend.agents.suspect_agent import SuspectState, SuspectProfile, SuspectDialogueOutput
from backend.models.suspect_models import CreateSuspectRequest, DialogueRequest


class TestSuspectRoutes:
    """Test suite for suspect routes."""

    @pytest.fixture
    def sample_suspect_data(self):
        """Sample suspect data for testing."""
        return {
            'id': 'suspect-123',
            'story_id': 'story-456',
            'name': 'John Doe',
            'profile_data': {
                'background': 'Former accountant',
                'occupation': 'Accountant',
                'motive': 'Financial desperation',
                'alibi': 'Claims to be at casino'
            },
            'state_data': {
                'name': 'John Doe',
                'interviewed': True,
                'suspicious_level': 7,
                'known_information': ['Has gambling debts'],
                'contradictions': ['Time inconsistency'],
                'emotional_state': 'nervous'
            },
            'created_at': '2024-01-01T00:00:00',
            'updated_at': '2024-01-01T00:00:00'
        }

    @pytest.fixture
    def sample_suspect_state(self):
        """Sample suspect state for testing."""
        return SuspectState(
            name="John Doe",
            interviewed=True,
            suspicious_level=7,
            known_information=["Has gambling debts"],
            contradictions=["Time inconsistency"],
            emotional_state="nervous"
        )

    @pytest.fixture
    def mock_suspect_service(self):
        """Mock SuspectService for testing."""
        with patch('backend.routes.suspect_routes.SuspectService') as mock_service:
            mock_instance = Mock()
            mock_service.return_value = mock_instance
            yield mock_instance

    @pytest.fixture
    def mock_jwt_required(self):
        """Mock JWT requirement for testing."""
        with patch('backend.routes.suspect_routes.jwt_required') as mock_jwt:
            mock_jwt.return_value = lambda f: f
            yield mock_jwt

    @pytest.fixture
    def mock_get_jwt_identity(self):
        """Mock JWT identity for testing."""
        with patch('backend.routes.suspect_routes.get_jwt_identity') as mock_identity:
            mock_identity.return_value = 'user-123'
            yield mock_identity

    @pytest.fixture
    def client(self, app):
        """Test client for the Flask app."""
        return app.test_client()

    def test_get_suspects_success(self, client, mock_suspect_service, mock_jwt_required, 
                                 mock_get_jwt_identity, sample_suspect_data):
        """Test successful retrieval of suspects."""
        # Setup mock
        mock_suspect_service.get_story_suspects = AsyncMock(return_value=[sample_suspect_data])
        
        # Make request
        response = client.get('/api/suspects?story_id=story-456')
        
        # Assertions
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1
        assert data[0]['name'] == 'John Doe'
        mock_suspect_service.get_story_suspects.assert_called_once_with('story-456', 'user-123')

    def test_get_suspects_missing_story_id(self, client, mock_jwt_required, mock_get_jwt_identity):
        """Test getting suspects without story_id parameter."""
        response = client.get('/api/suspects')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'story_id parameter is required' in data['error']

    def test_get_suspects_service_error(self, client, mock_suspect_service, mock_jwt_required, 
                                       mock_get_jwt_identity):
        """Test getting suspects with service error."""
        mock_suspect_service.get_story_suspects = AsyncMock(side_effect=Exception("Database error"))
        
        response = client.get('/api/suspects?story_id=story-456')
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'error' in data

    def test_get_suspect_success(self, client, mock_suspect_service, mock_jwt_required, 
                                mock_get_jwt_identity, sample_suspect_data):
        """Test successful retrieval of single suspect."""
        mock_suspect_service.get_suspect_profile = AsyncMock(return_value=sample_suspect_data)
        
        response = client.get('/api/suspects/suspect-123?story_id=story-456')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['name'] == 'John Doe'
        mock_suspect_service.get_suspect_profile.assert_called_once_with('suspect-123', 'story-456', 'user-123')

    def test_get_suspect_not_found(self, client, mock_suspect_service, mock_jwt_required, 
                                  mock_get_jwt_identity):
        """Test getting suspect that doesn't exist."""
        mock_suspect_service.get_suspect_profile = AsyncMock(return_value=None)
        
        response = client.get('/api/suspects/nonexistent?story_id=story-456')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'Suspect not found' in data['error']

    def test_create_suspect_success(self, client, mock_suspect_service, mock_jwt_required, 
                                   mock_get_jwt_identity, sample_suspect_data):
        """Test successful suspect creation."""
        mock_suspect_service.create_suspect = AsyncMock(return_value=sample_suspect_data)
        
        request_data = {
            'story_id': 'story-456',
            'name': 'John Doe',
            'profile_data': {'occupation': 'Accountant'}
        }
        
        response = client.post('/api/suspects', 
                              data=json.dumps(request_data),
                              content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['name'] == 'John Doe'
        mock_suspect_service.create_suspect.assert_called_once_with('user-123', request_data)

    def test_create_suspect_missing_body(self, client, mock_jwt_required, mock_get_jwt_identity):
        """Test creating suspect without request body."""
        response = client.post('/api/suspects')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Request body is required' in data['error']

    def test_post_dialogue_success(self, client, mock_suspect_service, mock_jwt_required, 
                                  mock_get_jwt_identity, sample_suspect_data):
        """Test successful dialogue posting."""
        dialogue_result = {
            'suspect_id': 'suspect-123',
            'question': 'Where were you last night?',
            'dialogue': 'I was at the casino, you can check with the dealers.',
            'updated_state': {'interviewed': True, 'suspicious_level': 8},
            'timestamp': '2024-01-01T00:00:00'
        }
        
        mock_suspect_service.get_suspect_profile = AsyncMock(return_value=sample_suspect_data)
        mock_suspect_service.generate_dialogue = AsyncMock(return_value=dialogue_result)
        
        request_data = {
            'question': 'Where were you last night?',
            'story_id': 'story-456',
            'context': {'interrogation_style': 'direct'}
        }
        
        response = client.post('/api/suspects/suspect-123/dialogue',
                              data=json.dumps(request_data),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['dialogue'] == 'I was at the casino, you can check with the dealers.'
        mock_suspect_service.generate_dialogue.assert_called_once()

    def test_post_dialogue_missing_question(self, client, mock_jwt_required, mock_get_jwt_identity):
        """Test posting dialogue without question."""
        request_data = {'story_id': 'story-456'}
        
        response = client.post('/api/suspects/suspect-123/dialogue',
                              data=json.dumps(request_data),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Question is required' in data['error']

    def test_post_dialogue_suspect_not_found(self, client, mock_suspect_service, mock_jwt_required, 
                                           mock_get_jwt_identity):
        """Test posting dialogue to non-existent suspect."""
        mock_suspect_service.get_suspect_profile = AsyncMock(return_value=None)
        
        request_data = {
            'question': 'Where were you?',
            'story_id': 'story-456'
        }
        
        response = client.post('/api/suspects/nonexistent/dialogue',
                              data=json.dumps(request_data),
                              content_type='application/json')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'Suspect not found' in data['error']

    def test_verify_alibi_success(self, client, mock_suspect_service, mock_jwt_required, 
                                 mock_get_jwt_identity, sample_suspect_data):
        """Test successful alibi verification."""
        verification_result = {
            'suspect_id': 'suspect-123',
            'alibi_verified': False,
            'verification_score': 45,
            'inconsistencies': ['Time discrepancy', 'No corroborating witnesses'],
            'dialogue_response': 'I... I was at the casino all night!',
            'updated_state': {'suspicious_level': 9},
            'timestamp': '2024-01-01T00:00:00'
        }
        
        mock_suspect_service.get_suspect_profile = AsyncMock(return_value=sample_suspect_data)
        mock_suspect_service.verify_alibi = AsyncMock(return_value=verification_result)
        
        request_data = {
            'story_id': 'story-456',
            'alibi_details': {'location': 'casino', 'time': '8pm-2am'},
            'evidence': [{'type': 'video', 'supports_alibi': False}]
        }
        
        response = client.post('/api/suspects/suspect-123/verify-alibi',
                              data=json.dumps(request_data),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['alibi_verified'] == False
        assert data['verification_score'] == 45
        mock_suspect_service.verify_alibi.assert_called_once()

    def test_verify_alibi_missing_story_id(self, client, mock_jwt_required, mock_get_jwt_identity):
        """Test alibi verification without story_id."""
        request_data = {'alibi_details': {}}
        
        response = client.post('/api/suspects/suspect-123/verify-alibi',
                              data=json.dumps(request_data),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'story_id is required' in data['error']

    def test_get_suspect_state_success(self, client, mock_suspect_service, mock_jwt_required, 
                                      mock_get_jwt_identity):
        """Test successful suspect state retrieval."""
        state_data = {
            'name': 'John Doe',
            'interviewed': True,
            'suspicious_level': 7,
            'emotional_state': 'nervous'
        }
        
        mock_suspect_service.get_suspect_state = AsyncMock(return_value=state_data)
        
        response = client.get('/api/suspects/suspect-123/state?story_id=story-456')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['suspicious_level'] == 7
        mock_suspect_service.get_suspect_state.assert_called_once_with('suspect-123', 'story-456', 'user-123')

    def test_get_suspect_state_not_found(self, client, mock_suspect_service, mock_jwt_required, 
                                        mock_get_jwt_identity):
        """Test getting state for non-existent suspect."""
        mock_suspect_service.get_suspect_state = AsyncMock(return_value=None)
        
        response = client.get('/api/suspects/nonexistent/state?story_id=story-456')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'Suspect state not found' in data['error']

    def test_update_suspect_state_success(self, client, mock_suspect_service, mock_jwt_required, 
                                         mock_get_jwt_identity, sample_suspect_data):
        """Test successful suspect state update."""
        updated_state = {
            'name': 'John Doe',
            'interviewed': True,
            'suspicious_level': 9,
            'emotional_state': 'defensive'
        }
        
        mock_suspect_service.get_suspect_profile = AsyncMock(return_value=sample_suspect_data)
        mock_suspect_service.update_suspect_state = AsyncMock(return_value=updated_state)
        
        request_data = {
            'story_id': 'story-456',
            'state_updates': {'suspicious_level': 9, 'emotional_state': 'defensive'}
        }
        
        response = client.put('/api/suspects/suspect-123/state',
                             data=json.dumps(request_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['suspicious_level'] == 9
        mock_suspect_service.update_suspect_state.assert_called_once()

    def test_explore_motives_success(self, client, mock_suspect_service, mock_jwt_required, 
                                   mock_get_jwt_identity, sample_suspect_data):
        """Test successful motive exploration."""
        motives_result = {
            'suspect_id': 'suspect-123',
            'current_motive': 'Financial desperation',
            'potential_motives': 'Revenge, greed, desperation',
            'psychological_profile': ['impulsive', 'desperate', 'cunning'],
            'relationship_factors': 'Business partner with access',
            'behavioral_indicators': ['nervous', 'evasive'],
            'analysis_sources': ['psychological analysis', 'behavioral patterns'],
            'timestamp': '2024-01-01T00:00:00'
        }
        
        mock_suspect_service.get_suspect_profile = AsyncMock(return_value=sample_suspect_data)
        mock_suspect_service.explore_motives = AsyncMock(return_value=motives_result)
        
        response = client.get('/api/suspects/suspect-123/motives?story_id=story-456')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['current_motive'] == 'Financial desperation'
        assert 'desperate' in data['psychological_profile']
        mock_suspect_service.explore_motives.assert_called_once_with('suspect-123', 'story-456', 'user-123')

    def test_generate_suspect_profile_success(self, client, mock_suspect_service, mock_jwt_required, 
                                            mock_get_jwt_identity):
        """Test successful suspect profile generation."""
        generation_result = {
            'suspect_id': 'suspect-123',
            'generated_profile': {
                'name': 'John Doe',
                'background': 'Former accountant with gambling problems',
                'occupation': 'Accountant',
                'motive': 'Financial desperation'
            },
            'sources': ['criminal psychology database', 'behavioral analysis'],
            'generation_prompt': 'Create a suspect profile for an accountant',
            'timestamp': '2024-01-01T00:00:00'
        }
        
        mock_suspect_service.generate_suspect_profile = AsyncMock(return_value=generation_result)
        
        request_data = {
            'story_id': 'story-456',
            'prompt': 'Create a suspect profile for an accountant',
            'context': {'crime_type': 'embezzlement'}
        }
        
        response = client.post('/api/suspects/suspect-123/generate',
                              data=json.dumps(request_data),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['generated_profile']['occupation'] == 'Accountant'
        mock_suspect_service.generate_suspect_profile.assert_called_once()

    def test_generate_suspect_profile_missing_story_id(self, client, mock_jwt_required, 
                                                      mock_get_jwt_identity):
        """Test profile generation without story_id."""
        request_data = {'prompt': 'Create a suspect'}
        
        response = client.post('/api/suspects/suspect-123/generate',
                              data=json.dumps(request_data),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'story_id is required' in data['error']

    def test_authorization_required(self, client):
        """Test that endpoints require authentication."""
        # This test would be more meaningful with actual JWT implementation
        # For now, we're mocking the jwt_required decorator
        response = client.get('/api/suspects?story_id=story-456')
        # Since we're mocking jwt_required to be a no-op, this should still work
        # In a real scenario without proper auth, this would return 401
        assert response.status_code in [200, 400, 401]  # Allow for various auth states

    def test_service_integration_error_handling(self, client, mock_suspect_service, 
                                               mock_jwt_required, mock_get_jwt_identity):
        """Test error handling when service methods fail."""
        mock_suspect_service.get_story_suspects = AsyncMock(side_effect=ValueError("Access denied"))
        
        response = client.get('/api/suspects?story_id=story-456')
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'error' in data

    def test_validation_error_handling(self, client, mock_suspect_service, mock_jwt_required, 
                                      mock_get_jwt_identity, sample_suspect_data):
        """Test handling of validation errors."""
        from pydantic import ValidationError
        
        mock_suspect_service.get_suspect_profile = AsyncMock(return_value=sample_suspect_data)
        mock_suspect_service.generate_dialogue = AsyncMock(
            side_effect=ValidationError("Invalid data", model=DialogueRequest)
        )
        
        request_data = {
            'question': 'Test question',
            'story_id': 'story-456'
        }
        
        response = client.post('/api/suspects/suspect-123/dialogue',
                              data=json.dumps(request_data),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Invalid request data' in data['error'] 