import json
import pytest
from unittest.mock import patch, MagicMock

from app import app
from models.template_models import MysteryTemplate, Suspect, Clue

@pytest.fixture
def client():
    """Create a test client."""
    with app.test_client() as client:
        yield client

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

@patch('services.template_service.TemplateService')
def test_get_all_templates(mock_service, client):
    """Test retrieving all templates."""
    # Set up mock
    mock_instance = mock_service.return_value
    mock_instance.get_all_templates.return_value = [mock_template()]
    
    # Make request
    response = client.get('/api/templates')
    data = json.loads(response.data)
    
    # Assertions
    assert response.status_code == 200
    assert data['success'] is True
    assert len(data['templates']) == 1
    assert data['templates'][0]['title'] == "Test Mystery"
    
    # Verify service call
    mock_instance.get_all_templates.assert_called_once()

@patch('services.template_service.TemplateService')
def test_get_template_by_id(mock_service, client, mock_template):
    """Test retrieving a template by ID."""
    # Set up mock
    mock_instance = mock_service.return_value
    mock_instance.get_template_by_id.return_value = mock_template
    
    # Make request
    response = client.get('/api/templates/test-id-123')
    data = json.loads(response.data)
    
    # Assertions
    assert response.status_code == 200
    assert data['success'] is True
    assert data['template']['id'] == "test-id-123"
    
    # Verify service call
    mock_instance.get_template_by_id.assert_called_once_with("test-id-123")

@patch('services.template_service.TemplateService')
def test_get_template_not_found(mock_service, client):
    """Test retrieving a non-existent template."""
    # Set up mock
    mock_instance = mock_service.return_value
    mock_instance.get_template_by_id.return_value = None
    
    # Make request
    response = client.get('/api/templates/nonexistent-id')
    data = json.loads(response.data)
    
    # Assertions
    assert response.status_code == 404
    assert data['success'] is False
    assert "not found" in data['error']

@patch('services.template_service.TemplateService')
def test_create_template(mock_service, client, mock_template):
    """Test creating a new template."""
    # Set up mock
    mock_instance = mock_service.return_value
    mock_instance.create_template.return_value = mock_template
    
    # Prepare test data
    template_data = mock_template.model_dump()
    
    # Make request
    response = client.post('/api/templates', 
                          json=template_data,
                          content_type='application/json')
    data = json.loads(response.data)
    
    # Assertions
    assert response.status_code == 201
    assert data['success'] is True
    assert data['template']['title'] == "Test Mystery"
    
    # Verify service call (simplified check)
    assert mock_instance.create_template.called

@patch('services.template_service.TemplateService')
def test_update_template(mock_service, client, mock_template):
    """Test updating a template."""
    # Set up mock
    mock_instance = mock_service.return_value
    mock_instance.get_template_by_id.return_value = mock_template
    mock_instance.update_template.return_value = mock_template
    
    # Prepare update data
    update_data = {
        "title": "Updated Mystery Title",
        "description": "Updated description"
    }
    
    # Make request
    response = client.put('/api/templates/test-id-123', 
                         json=update_data,
                         content_type='application/json')
    data = json.loads(response.data)
    
    # Assertions
    assert response.status_code == 200
    assert data['success'] is True
    
    # Verify service calls
    mock_instance.get_template_by_id.assert_called_once_with("test-id-123")
    mock_instance.update_template.assert_called_once_with("test-id-123", update_data)

@patch('services.template_service.TemplateService')
def test_delete_template(mock_service, client, mock_template):
    """Test deleting a template."""
    # Set up mock
    mock_instance = mock_service.return_value
    mock_instance.get_template_by_id.return_value = mock_template
    mock_instance.delete_template.return_value = True
    
    # Make request
    response = client.delete('/api/templates/test-id-123')
    data = json.loads(response.data)
    
    # Assertions
    assert response.status_code == 200
    assert data['success'] is True
    assert "deleted successfully" in data['message']
    
    # Verify service calls
    mock_instance.get_template_by_id.assert_called_once_with("test-id-123")
    mock_instance.delete_template.assert_called_once_with("test-id-123") 