# NOTE: Uses global app/client fixtures from conftest.py. Do not import create_app or define app/client fixtures here.
import pytest
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4
from datetime import datetime
import os
from backend.tests.mocks.supabase_mock import MockSupabaseClient

@pytest.fixture
def mock_supabase():
    # Patch create_client in the actual service import path
    with patch('backend.services.supabase_service.create_client') as mock:
        mock_client = Mock()
        # Chainable methods
        mock_client.table.return_value = mock_client
        mock_client.select.return_value = mock_client
        mock_client.eq.return_value = mock_client
        mock_client.single.return_value = mock_client
        mock_client.insert.return_value = mock_client
        mock_client.update.return_value = mock_client
        # Do NOT set .execute here; set it in each test
        mock.return_value = mock_client
        yield mock

@pytest.fixture(autouse=True)
def patch_create_client(mock_supabase):
    with patch('backend.services.supabase_service.create_client', mock_supabase), \
         patch('backend.routes.clue_routes.create_client', mock_supabase):
        yield

@pytest.fixture
def sample_clue():
    return {
        'id': str(uuid4()),
        'story_id': str(uuid4()),
        'template_clue_id': str(uuid4()),
        'discovered_at': datetime.now().isoformat(),
        'discovery_method': 'search',
        'discovery_location': 'library',
        'relevance_score': 0.5,
        'is_red_herring': False,
        'notes': None,
        'connections': [],
        'type': 'physical',
        'description': 'A clue description',
        'location': 'library',
    }

@pytest.fixture
def sample_template_clue():
    return {
        'id': str(uuid4()),
        'type': 'physical',
        'description': 'A bloody knife',
        'location': 'kitchen',
        'is_red_herring': False
    }

def test_get_story_clues(client, shared_supabase_client, sample_clue):
    client, _ = client
    # Insert the sample clue into the mock DB
    shared_supabase_client.table('story_clues').insert(sample_clue)
    response = client.get(f'/api/stories/{sample_clue["story_id"]}/clues')
    if response.status_code != 200:
        print('DEBUG: status_code', response.status_code)
        print('DEBUG: data', response.get_data(as_text=True))
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['id'] == sample_clue['id']

def test_discover_clue(client, mock_supabase, sample_clue, sample_template_clue):
    client, _ = client
    """Test discovering a new clue."""
    # Ensure template clue has required fields
    sample_template_clue = {
        **sample_template_clue,
        'type': 'physical',
        'description': 'A bloody knife',
        'location': 'kitchen',
    }
    mock_template_result = Mock()
    mock_template_result.data = sample_template_clue
    chain_template = mock_supabase.return_value.table.return_value.select.return_value.eq.return_value.single.return_value
    chain_template.execute = AsyncMock(return_value=mock_template_result)
    # Inserted clue must have all required fields
    inserted_clue = {**sample_clue, 'type': 'physical', 'description': 'A clue description', 'location': 'library'}
    # Patch the discover_clue method to return the inserted_clue dict
    from backend.agents.models.clue_models import ClueDetail
    clue_model = ClueDetail(**inserted_clue)
    with patch('backend.services.clue_service.ClueService.discover_clue', AsyncMock(return_value=clue_model)):
        data = {
            'template_clue_id': sample_clue['template_clue_id'],
            'discovery_method': 'search',
            'discovery_location': 'library',
            'type': 'physical',
            'description': 'A clue description',
        }
        response = client.post(f'/api/stories/{sample_clue["story_id"]}/clues', json=data)
        if response.status_code != 201:
            print('DEBUG: status_code', response.status_code)
            print('DEBUG: data', response.get_data(as_text=True))
        assert response.status_code == 201
        assert response.json['id'] == sample_clue['id']

def test_discover_clue_missing_fields(client, mock_supabase, sample_clue):
    client, _ = client
    """Test discovering a clue with missing required fields."""
    data = {
        'template_clue_id': sample_clue['template_clue_id']
        # Missing discovery_method and discovery_location
    }
    response = client.post(f'/api/stories/{sample_clue["story_id"]}/clues', json=data)
    assert response.status_code == 400
    assert 'error' in response.json
    assert 'Missing required fields' in response.json['error']

def test_update_clue_notes(client, mock_supabase, sample_clue):
    client, _ = client
    """Test updating notes for a clue."""
    updated_clue = {
        'id': sample_clue['id'],
        'story_id': sample_clue['story_id'],
        'template_clue_id': sample_clue['template_clue_id'],
        'discovered_at': sample_clue['discovered_at'],
        'discovery_method': sample_clue['discovery_method'],
        'discovery_location': sample_clue['discovery_location'],
        'relevance_score': 0.5,
        'is_red_herring': False,
        'notes': 'This is a test note',
        'connections': [],
        'type': 'physical',
        'description': 'A clue description',
        'location': 'library',
    }
    mock_get_clue_result = AsyncMock(return_value=sample_clue)
    mock_update_result = AsyncMock(return_value=updated_clue)
    with patch('backend.services.clue_service.ClueService.get_clue_details_by_id', mock_get_clue_result), \
         patch('backend.services.clue_service.ClueService.update_clue_notes', mock_update_result):
        data = {'notes': 'This is a test note'}
        response = client.put(f'/api/clues/{sample_clue["id"]}/notes', json=data)
        if response.status_code != 200:
            print('DEBUG: status_code', response.status_code)
            print('DEBUG: data', response.get_data(as_text=True))
        assert response.status_code == 200
        assert response.json['notes'] == 'This is a test note'

def test_add_clue_connection(client, mock_supabase, sample_clue):
    client, _ = client
    """Test adding a connection between clues."""
    connected_clue_id = str(uuid4())
    connection = {
        'connected_clue_id': connected_clue_id,
        'connection_type': 'related',
        'details': {'reason': 'Found together'},
        'created_at': datetime.now().isoformat(),
        'story_id': sample_clue['story_id'],
        'source_clue_id': sample_clue['id'],
        'target_clue_id': connected_clue_id,
        'relationship_type': 'related',
        'description': 'Found together',
        'id': str(uuid4()),
    }
    updated_clue = {
        'id': sample_clue['id'],
        'story_id': sample_clue['story_id'],
        'template_clue_id': sample_clue['template_clue_id'],
        'discovered_at': sample_clue['discovered_at'],
        'discovery_method': sample_clue['discovery_method'],
        'discovery_location': sample_clue['discovery_location'],
        'relevance_score': 0.5,
        'is_red_herring': False,
        'notes': sample_clue['notes'],
        'connections': [connection],
        'type': 'physical',
        'description': 'A clue description',
        'location': 'library',
    }
    mock_select_result = AsyncMock(return_value=sample_clue)
    mock_update_result = AsyncMock(return_value=updated_clue)
    with patch('backend.services.clue_service.ClueService.get_clue_details_by_id', mock_select_result), \
         patch('backend.services.clue_service.ClueService.add_clue_connection', mock_update_result):
        data = {
            'connected_clue_id': connected_clue_id,
            'connection_type': 'related',
            'connection_details': {'reason': 'Found together'},
            'story_id': sample_clue['story_id'],
        }
        response = client.post(f'/api/clues/{sample_clue["id"]}/connections', json=data)
        if response.status_code != 201:
            print('DEBUG: status_code', response.status_code)
            print('DEBUG: data', response.get_data(as_text=True))
        assert response.status_code == 201
        assert len(response.json['connections']) == 1
        assert response.json['connections'][0]['connected_clue_id'] == connected_clue_id

def test_update_clue_relevance(client, mock_supabase, sample_clue):
    client, _ = client
    """Test updating a clue's relevance score."""
    updated_clue = {
        'id': sample_clue['id'],
        'story_id': sample_clue['story_id'],
        'template_clue_id': sample_clue['template_clue_id'],
        'discovered_at': sample_clue['discovered_at'],
        'discovery_method': sample_clue['discovery_method'],
        'discovery_location': sample_clue['discovery_location'],
        'relevance_score': 0.8,
        'is_red_herring': False,
        'notes': sample_clue['notes'],
        'connections': [],
        'type': 'physical',
        'description': 'A clue description',
        'location': 'library',
    }
    mock_get_clue_result = AsyncMock(return_value=sample_clue)
    mock_update_result = AsyncMock(return_value=updated_clue)
    with patch('backend.services.clue_service.ClueService.get_clue_details_by_id', mock_get_clue_result), \
         patch('backend.services.clue_service.ClueService.update_clue_relevance', mock_update_result):
        data = {'relevance_score': 0.8}
        response = client.put(f'/api/clues/{sample_clue["id"]}/relevance', json=data)
        if response.status_code != 200:
            print('DEBUG: status_code', response.status_code)
            print('DEBUG: data', response.get_data(as_text=True))
        assert response.status_code == 200
        assert response.json['relevance_score'] == 0.8

def test_get_clue_connections(client, mock_supabase, sample_clue):
    client, _ = client
    """Test getting all connections for a clue."""
    connections = [
        {
            'connected_clue_id': str(uuid4()),
            'connection_type': 'related',
            'details': {'reason': 'Found together'},
            'created_at': datetime.now().isoformat(),
            'story_id': sample_clue['story_id'],
            'source_clue_id': sample_clue['id'],
            'target_clue_id': str(uuid4()),
            'relationship_type': 'related',
            'description': 'Found together',
            'id': str(uuid4()),
        }
    ]
    mock_get_clue_result = AsyncMock(return_value=sample_clue)
    mock_connections_result = AsyncMock(return_value=connections)
    with patch('backend.services.clue_service.ClueService.get_clue_details_by_id', mock_get_clue_result), \
         patch('backend.services.clue_service.ClueService.get_clue_connections', mock_connections_result):
        response = client.get(f'/api/clues/{sample_clue["id"]}/connections')
        if response.status_code != 200:
            print('DEBUG: status_code', response.status_code)
            print('DEBUG: data', response.get_data(as_text=True))
        assert response.status_code == 200
        assert isinstance(response.json, list)
        assert len(response.json) == 1

def test_mark_clue_as_red_herring(client, mock_supabase, sample_clue):
    client, _ = client
    """Test marking a clue as a red herring."""
    updated_clue = {
        'id': sample_clue['id'],
        'story_id': sample_clue['story_id'],
        'template_clue_id': sample_clue['template_clue_id'],
        'discovered_at': sample_clue['discovered_at'],
        'discovery_method': sample_clue['discovery_method'],
        'discovery_location': sample_clue['discovery_location'],
        'relevance_score': 0.5,
        'is_red_herring': True,
        'notes': sample_clue['notes'],
        'connections': [],
        'type': 'physical',
        'description': 'A clue description',
        'location': 'library',
    }
    mock_get_clue_result = AsyncMock(return_value=sample_clue)
    mock_update_result = AsyncMock(return_value=updated_clue)
    with patch('backend.services.clue_service.ClueService.get_clue_details_by_id', mock_get_clue_result), \
         patch('backend.services.clue_service.ClueService.mark_clue_as_red_herring', mock_update_result):
        data = {'is_red_herring': True}
        response = client.put(f'/api/clues/{sample_clue["id"]}/red-herring', json=data)
        if response.status_code != 200:
            print('DEBUG: status_code', response.status_code)
            print('DEBUG: data', response.get_data(as_text=True))
        assert response.status_code == 200
        assert response.json['is_red_herring'] is True

def test_clue_not_found(client, mock_supabase):
    client, _ = client
    """Test handling of non-existent clue."""
    mock_get_clue_result = AsyncMock(return_value=None)
    with patch('backend.services.clue_service.ClueService.get_clue_details_by_id', mock_get_clue_result):
        response = client.get(f'/api/clues/{uuid4()}/connections')
        assert response.status_code == 404
        assert 'error' in response.json

@pytest.fixture
def shared_supabase_client():
    return MockSupabaseClient()

@pytest.fixture(autouse=True)
def patch_supabase_client(shared_supabase_client):
    with patch('backend.services.supabase_service.get_supabase_client', return_value=shared_supabase_client), \
         patch('backend.routes.clue_routes.get_supabase_client', return_value=shared_supabase_client):
        yield 