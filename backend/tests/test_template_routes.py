# NOTE: Uses global app/client fixtures from conftest.py. Do not import create_app or define app/client fixtures here.
import json
import pytest
from unittest.mock import patch, MagicMock

from backend.agents.models.template_models import MysteryTemplate, Suspect, Clue

@pytest.fixture
def mock_supabase():
    with patch('services.template_service.create_client') as mock_create_client:
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client
        yield mock_client

@pytest.fixture
def mock_template():
    """Create a sample template for testing."""
    return MysteryTemplate(
        id="test-id-123",
        title="Test Mystery",
        description="A test mystery case",
        setting="Small town",
        time_period="Modern day",
        victim={"name": "John Doe", "description": "Local businessman"},
        suspects=[
            Suspect(
                name="Alice Smith",
                description="Town resident",
                motive="Financial dispute",
                alibi="Was at home",
                guilty=False
            ),
            Suspect(
                name="Bob Johnson",
                description="Business partner",
                motive="Inheritance",
                alibi="Out of town",
                guilty=True
            )
        ],
        clues=[
            Clue(
                id="clue-1",
                description="Broken watch",
                location="Crime scene",
                related_suspects=["Alice Smith"],
                type="physical"
            ),
            Clue(
                id="clue-2",
                description="Missing money",
                location="Office",
                related_suspects=["Bob Johnson"],
                type="observation"
            )
        ]
    )

@pytest.fixture
def sample_template():
    return {
        "id": "test-id-123",
        "title": "The Mansion Murder",
        "description": "A wealthy businessman is found dead in his mansion",
        "setting": "Victorian mansion",
        "time_period": "1920s",
        "victim": {
            "name": "John Smith",
            "occupation": "Businessman",
            "cause_of_death": "Poisoning"
        },
        "suspects": [
            {
                "name": "Mary Johnson",
                "description": "The victim's wife",
                "motive": "Inheritance",
                "alibi": "Was at a party",
                "guilty": False,
                "personality_traits": {
                    "ambitious": 0.8,
                    "deceptive": 0.6
                }
            }
        ],
        "clues": [
            {
                "id": "clue1",
                "description": "A half-empty wine glass",
                "location": "Victim's study",
                "related_suspects": ["Mary Johnson"],
                "discovery_difficulty": 0.5,
                "type": "physical"
            }
        ],
        "red_herrings": [
            {
                "description": "A broken window",
                "explanation": "Was broken during a storm"
            }
        ],
        "difficulty": 0.7,
        "estimated_duration": "2 hours"
    }

@patch('routes.template_routes.template_service')
def test_get_all_templates(mock_service, client, sample_template):
    mock_service.get_all_templates.return_value = [MysteryTemplate(**sample_template)]
    response = client.get('/api/templates')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'success' in data
    assert 'templates' in data
    assert 'count' in data
    assert isinstance(data['templates'], list)
    assert data['templates'][0]['title'] == sample_template['title']

@patch('routes.template_routes.template_service')
def test_get_template_by_id(mock_service, client, sample_template):
    mock_service.get_template_by_id.return_value = MysteryTemplate(**sample_template)
    response = client.get(f"/api/templates/{sample_template['id']}")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success']
    assert data['template']['id'] == sample_template['id']

@patch('routes.template_routes.template_service')
def test_get_template_not_found(mock_service, client):
    mock_service.get_template_by_id.return_value = None
    response = client.get('/api/templates/nonexistent')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert not data['success']
    assert data['error'] == 'Template not found'

@patch('routes.template_routes.template_service')
def test_create_template_success(mock_service, client, sample_template):
    mock_service.create_template.return_value = MysteryTemplate(**sample_template)
    response = client.post(
        '/api/templates',
        json=sample_template,
        headers={'Content-Type': 'application/json'}
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['success']
    assert data['template']['title'] == sample_template['title']

@patch('routes.template_routes.template_service')
def test_create_template_invalid_data(mock_service, client):
    invalid_template = {
        "title": "Invalid Template"
        # Missing required fields
    }
    response = client.post(
        '/api/templates',
        json=invalid_template,
        headers={'Content-Type': 'application/json'}
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert not data['success']
    assert data['error'] == 'Validation error'

@patch('routes.template_routes.template_service')
def test_update_template_success(mock_service, client, sample_template):
    mock_service.get_template_by_id.return_value = MysteryTemplate(**sample_template)
    mock_service.update_template.return_value = MysteryTemplate(**sample_template)
    update_data = {"title": "Updated Title", "description": "Updated desc"}
    response = client.put(
        f"/api/templates/{sample_template['id']}",
        json=update_data,
        headers={'Content-Type': 'application/json'}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success']
    assert data['template']['title'] == sample_template['title']

@patch('routes.template_routes.template_service')
def test_update_template_not_found(mock_service, client, sample_template):
    mock_service.get_template_by_id.return_value = None
    response = client.put(
        '/api/templates/nonexistent',
        json=sample_template,
        headers={'Content-Type': 'application/json'}
    )
    assert response.status_code == 404
    data = json.loads(response.data)
    assert not data['success']
    assert data['error'] == 'Template not found'

@patch('routes.template_routes.template_service')
def test_delete_template_success(mock_service, client, sample_template):
    mock_service.get_template_by_id.return_value = MysteryTemplate(**sample_template)
    mock_service.delete_template.return_value = True
    response = client.delete(f"/api/templates/{sample_template['id']}")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success']
    assert 'deleted successfully' in data['message']

@patch('routes.template_routes.template_service')
def test_delete_template_not_found(mock_service, client):
    mock_service.get_template_by_id.return_value = None
    response = client.delete('/api/templates/nonexistent')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert not data['success']
    assert data['error'] == 'Template not found'

@patch('routes.template_routes.template_service')
def test_search_templates_no_query(mock_service, client):
    response = client.get('/api/templates/search')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert not data['success']
    assert data['error'] == 'Search query is required'

@patch('routes.template_routes.template_service')
def test_search_templates_with_query(mock_service, client, sample_template):
    mock_service.search_templates.return_value = [MysteryTemplate(**sample_template)]
    response = client.get('/api/templates/search?q=mansion')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success']
    assert isinstance(data['templates'], list)
    assert data['templates'][0]['title'] == sample_template['title'] 