# NOTE: Uses global app/client fixtures from conftest.py. Do not import create_app or define app/client fixtures here.
import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from datetime import datetime

@pytest.fixture
def mock_supabase():
    with patch('routes.clue_routes.create_client') as mock:
        yield mock

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
        'connections': []
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

@pytest.mark.asyncio
async def test_get_story_clues(client, mock_supabase, sample_clue):
    """Test getting all clues for a story."""
    mock_supabase.return_value.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [sample_clue]
    
    response = await client.get(f'/api/stories/{sample_clue["story_id"]}/clues')
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['id'] == sample_clue['id']

@pytest.mark.asyncio
async def test_discover_clue(client, mock_supabase, sample_clue, sample_template_clue):
    """Test discovering a new clue."""
    mock_supabase.return_value.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = sample_template_clue
    mock_supabase.return_value.table.return_value.insert.return_value.execute.return_value.data = [sample_clue]
    
    data = {
        'template_clue_id': sample_clue['template_clue_id'],
        'discovery_method': 'search',
        'discovery_location': 'library'
    }
    
    response = await client.post(f'/api/stories/{sample_clue["story_id"]}/clues', json=data)
    assert response.status_code == 201
    assert response.json['id'] == sample_clue['id']

@pytest.mark.asyncio
async def test_discover_clue_missing_fields(client, mock_supabase, sample_clue):
    """Test discovering a clue with missing required fields."""
    data = {
        'template_clue_id': sample_clue['template_clue_id']
        # Missing discovery_method and discovery_location
    }
    
    response = await client.post(f'/api/stories/{sample_clue["story_id"]}/clues', json=data)
    assert response.status_code == 400
    assert 'error' in response.json
    assert 'Missing required fields' in response.json['error']

@pytest.mark.asyncio
async def test_update_clue_notes(client, mock_supabase, sample_clue):
    """Test updating notes for a clue."""
    updated_clue = {**sample_clue, 'notes': 'This is a test note'}
    mock_supabase.return_value.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [updated_clue]
    
    data = {'notes': 'This is a test note'}
    response = await client.put(f'/api/clues/{sample_clue["id"]}/notes', json=data)
    assert response.status_code == 200
    assert response.json['notes'] == 'This is a test note'

@pytest.mark.asyncio
async def test_add_clue_connection(client, mock_supabase, sample_clue):
    """Test adding a connection between clues."""
    connected_clue_id = str(uuid4())
    connection = {
        'connected_clue_id': connected_clue_id,
        'connection_type': 'related',
        'details': {'reason': 'Found together'}
    }
    
    mock_supabase.return_value.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = sample_clue
    updated_clue = {**sample_clue, 'connections': [connection]}
    mock_supabase.return_value.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [updated_clue]
    
    data = {
        'connected_clue_id': connected_clue_id,
        'connection_type': 'related',
        'connection_details': {'reason': 'Found together'}
    }
    
    response = await client.post(f'/api/clues/{sample_clue["id"]}/connections', json=data)
    assert response.status_code == 201
    assert len(response.json['connections']) == 1
    assert response.json['connections'][0]['connected_clue_id'] == connected_clue_id

@pytest.mark.asyncio
async def test_update_clue_relevance(client, mock_supabase, sample_clue):
    """Test updating a clue's relevance score."""
    updated_clue = {**sample_clue, 'relevance_score': 0.8}
    mock_supabase.return_value.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [updated_clue]
    
    data = {'relevance_score': 0.8}
    response = await client.put(f'/api/clues/{sample_clue["id"]}/relevance', json=data)
    assert response.status_code == 200
    assert response.json['relevance_score'] == 0.8

@pytest.mark.asyncio
async def test_get_clue_connections(client, mock_supabase, sample_clue):
    """Test getting all connections for a clue."""
    connections = [
        {
            'connected_clue_id': str(uuid4()),
            'connection_type': 'related',
            'details': {'reason': 'Found together'},
            'created_at': datetime.now().isoformat()
        }
    ]
    mock_supabase.return_value.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {'connections': connections}
    
    response = await client.get(f'/api/clues/{sample_clue["id"]}/connections')
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['connection_type'] == 'related'

@pytest.mark.asyncio
async def test_mark_clue_as_red_herring(client, mock_supabase, sample_clue):
    """Test marking a clue as a red herring."""
    updated_clue = {**sample_clue, 'is_red_herring': True}
    mock_supabase.return_value.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [updated_clue]
    
    data = {'is_red_herring': True}
    response = await client.put(f'/api/clues/{sample_clue["id"]}/red-herring', json=data)
    assert response.status_code == 200
    assert response.json['is_red_herring'] is True

@pytest.mark.asyncio
async def test_clue_not_found(client, mock_supabase):
    """Test handling of non-existent clue."""
    mock_supabase.return_value.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = None
    
    response = await client.get(f'/api/clues/{uuid4()}/connections')
    assert response.status_code == 404
    assert 'error' in response.json 