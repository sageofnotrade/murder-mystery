import pytest
from unittest.mock import patch, MagicMock
from backend.services.story_service import StoryService
from backend.services.supabase_service import get_supabase_client
from utils.error_handlers import (
    ValidationError, ResourceNotFoundError,
    AuthenticationError, AuthorizationError
)
import json

@pytest.fixture
def mock_supabase_auth():
    """Mock Supabase authentication."""
    with patch('backend.services.supabase_service.get_supabase_client') as mock_client:
        mock_client.return_value = MagicMock()
        yield mock_client.return_value

@pytest.fixture
def story_service(mock_supabase_auth):
    """Create a StoryService instance with mocked Supabase client."""
    return StoryService(mock_supabase_auth)

class TestStoryEdgeCases:
    """Test edge cases for story operations."""

    def test_create_story_empty_title(self, story_service):
        """Test creating a story with an empty title."""
        with pytest.raises(ValidationError) as exc_info:
            story_service.create_story({
                "title": "",
                "description": "Test description",
                "genre": "mystery",
                "difficulty": "medium"
            })
        assert "title" in str(exc_info.value).lower()

    def test_create_story_missing_required_fields(self, story_service):
        """Test creating a story with missing required fields."""
        with pytest.raises(ValidationError) as exc_info:
            story_service.create_story({
                "title": "Test Story"
                # Missing description, genre, and difficulty
            })
        assert "missing required fields" in str(exc_info.value).lower()

    def test_create_story_invalid_genre(self, story_service):
        """Test creating a story with an invalid genre."""
        with pytest.raises(ValidationError) as exc_info:
            story_service.create_story({
                "title": "Test Story",
                "description": "Test description",
                "genre": "invalid_genre",
                "difficulty": "medium"
            })
        assert "genre" in str(exc_info.value).lower()

    def test_create_story_invalid_difficulty(self, story_service):
        """Test creating a story with an invalid difficulty level."""
        with pytest.raises(ValidationError) as exc_info:
            story_service.create_story({
                "title": "Test Story",
                "description": "Test description",
                "genre": "mystery",
                "difficulty": "invalid_difficulty"
            })
        assert "difficulty" in str(exc_info.value).lower()

    def test_get_story_invalid_uuid(self, story_service):
        """Test getting a story with an invalid UUID."""
        with pytest.raises(ValidationError) as exc_info:
            story_service.get_story_sync("invalid-uuid", "user123")
        assert "invalid" in str(exc_info.value).lower()

    def test_get_story_nonexistent(self, story_service, mock_supabase_auth):
        """Test getting a nonexistent story."""
        mock_supabase_auth.table().select().eq().execute.return_value = {
            "data": None,
            "error": "Not found"
        }
        with pytest.raises(ResourceNotFoundError) as exc_info:
            story_service.get_story_sync("123e4567-e89b-12d3-a456-426614174000", "user123")
        assert "not found" in str(exc_info.value).lower()

    def test_update_story_unauthorized(self, story_service, mock_supabase_auth):
        """Test updating a story without authorization."""
        mock_supabase_auth.table().select().eq().execute.return_value = {
            "data": [{"user_id": "different_user"}],
            "error": None
        }
        with pytest.raises(AuthorizationError) as exc_info:
            story_service.update_story(
                "123e4567-e89b-12d3-a456-426614174000",
                {"title": "New Title"},
                "user123"
            )
        assert "unauthorized" in str(exc_info.value).lower()

    def test_delete_story_nonexistent(self, story_service, mock_supabase_auth):
        """Test deleting a nonexistent story."""
        mock_supabase_auth.table().select().eq().execute.return_value = {
            "data": None,
            "error": "Not found"
        }
        with pytest.raises(ResourceNotFoundError) as exc_info:
            story_service.delete_story("123e4567-e89b-12d3-a456-426614174000", "user123")
        assert "not found" in str(exc_info.value).lower()

    def test_perform_action_invalid_story_state(self, story_service, mock_supabase_auth):
        """Test performing an action when story is in invalid state."""
        mock_supabase_auth.table().select().eq().execute.return_value = {
            "data": [{"state": "completed"}],
            "error": None
        }
        with pytest.raises(ValidationError) as exc_info:
            story_service.perform_action(
                "123e4567-e89b-12d3-a456-426614174000",
                "user123",
                {"action": "investigate", "target": "clue_1"}
            )
        assert "invalid state" in str(exc_info.value).lower()

    def test_make_choice_invalid_option(self, story_service, mock_supabase_auth):
        """Test making a choice with an invalid option."""
        mock_supabase_auth.table().select().eq().execute.return_value = {
            "data": [{"current_choices": ["option1", "option2"]}],
            "error": None
        }
        with pytest.raises(ValidationError) as exc_info:
            story_service.make_choice(
                "123e4567-e89b-12d3-a456-426614174000",
                "user123",
                {"choice": "invalid_option"}
            )
        assert "invalid choice" in str(exc_info.value).lower()

    def test_get_stories_invalid_user(self, story_service, mock_supabase_auth):
        """Test getting stories for an invalid user."""
        mock_supabase_auth.table().select().eq().execute.return_value = {
            "data": None,
            "error": "Invalid user"
        }
        with pytest.raises(ResourceNotFoundError) as exc_info:
            story_service.get_user_stories("invalid_user")
        assert "not found" in str(exc_info.value).lower()

    def test_create_story_duplicate_title(self, story_service, mock_supabase_auth):
        """Test creating a story with a duplicate title."""
        mock_supabase_auth.table().select().eq().execute.return_value = {
            "data": [{"title": "Existing Story"}],
            "error": None
        }
        with pytest.raises(ValidationError) as exc_info:
            story_service.create_story({
                "title": "Existing Story",
                "description": "Test description",
                "genre": "mystery",
                "difficulty": "medium"
            })
        assert "already exists" in str(exc_info.value).lower()

    def test_update_story_invalid_data(self, story_service, mock_supabase_auth):
        """Test updating a story with invalid data."""
        mock_supabase_auth.table().select().eq().execute.return_value = {
            "data": [{"user_id": "user123"}],
            "error": None
        }
        with pytest.raises(ValidationError) as exc_info:
            story_service.update_story(
                "123e4567-e89b-12d3-a456-426614174000",
                {"genre": "invalid_genre"},
                "user123"
            )
        assert "invalid" in str(exc_info.value).lower()

    def test_get_story_progress_invalid_story(self, story_service, mock_supabase_auth):
        """Test getting progress for an invalid story."""
        mock_supabase_auth.table().select().eq().execute.return_value = {
            "data": None,
            "error": "Not found"
        }
        with pytest.raises(ResourceNotFoundError) as exc_info:
            story_service.get_story_progress("123e4567-e89b-12d3-a456-426614174000", "user123")
        assert "not found" in str(exc_info.value).lower()

    def test_perform_action_invalid_action(self, story_service, mock_supabase_auth):
        """Test performing an invalid action."""
        mock_supabase_auth.table().select().eq().execute.return_value = {
            "data": [{"state": "active"}],
            "error": None
        }
        with pytest.raises(ValidationError) as exc_info:
            story_service.perform_action(
                "123e4567-e89b-12d3-a456-426614174000",
                "user123",
                {"action": "invalid_action", "target": "clue_1"}
            )
        assert "invalid action" in str(exc_info.value).lower()

    def test_make_choice_no_choices_available(self, story_service, mock_supabase_auth):
        """Test making a choice when no choices are available."""
        mock_supabase_auth.table().select().eq().execute.return_value = {
            "data": [{"current_choices": []}],
            "error": None
        }
        with pytest.raises(ValidationError) as exc_info:
            story_service.make_choice(
                "123e4567-e89b-12d3-a456-426614174000",
                "user123",
                {"choice": "option1"}
            )
        assert "no choices available" in str(exc_info.value).lower()

    def test_create_story_title_too_long(self, story_service):
        """Test creating a story with a title that exceeds maximum length."""
        with pytest.raises(ValidationError) as exc_info:
            story_service.create_story({
                "title": "a" * 256,  # Assuming max length is 255
                "description": "Test description",
                "genre": "mystery",
                "difficulty": "medium"
            })
        assert "title" in str(exc_info.value).lower()

    def test_create_story_description_too_long(self, story_service):
        """Test creating a story with a description that exceeds maximum length."""
        with pytest.raises(ValidationError) as exc_info:
            story_service.create_story({
                "title": "Test Story",
                "description": "a" * 10001,  # Assuming max length is 10000
                "genre": "mystery",
                "difficulty": "medium"
            })
        assert "description" in str(exc_info.value).lower()

    def test_perform_action_missing_target(self, story_service, mock_supabase_auth):
        """Test performing an action without specifying a target."""
        mock_supabase_auth.table().select().eq().execute.return_value = {
            "data": [{"state": "active"}],
            "error": None
        }
        with pytest.raises(ValidationError) as exc_info:
            story_service.perform_action(
                "123e4567-e89b-12d3-a456-426614174000",
                "user123",
                {"action": "investigate"}  # Missing target
            )
        assert "target" in str(exc_info.value).lower()

    def test_perform_action_missing_action(self, story_service, mock_supabase_auth):
        """Test performing an action without specifying the action type."""
        mock_supabase_auth.table().select().eq().execute.return_value = {
            "data": [{"state": "active"}],
            "error": None
        }
        with pytest.raises(ValidationError) as exc_info:
            story_service.perform_action(
                "123e4567-e89b-12d3-a456-426614174000",
                "user123",
                {"target": "clue_1"}  # Missing action
            )
        assert "action" in str(exc_info.value).lower()

    def test_make_choice_missing_choice(self, story_service, mock_supabase_auth):
        """Test making a choice without specifying the choice."""
        mock_supabase_auth.table().select().eq().execute.return_value = {
            "data": [{"current_choices": ["option1", "option2"]}],
            "error": None
        }
        with pytest.raises(ValidationError) as exc_info:
            story_service.make_choice(
                "123e4567-e89b-12d3-a456-426614174000",
                "user123",
                {}  # Empty choice data
            )
        assert "choice" in str(exc_info.value).lower()

    def test_update_story_empty_update(self, story_service, mock_supabase_auth):
        """Test updating a story with empty update data."""
        mock_supabase_auth.table().select().eq().execute.return_value = {
            "data": [{"user_id": "user123"}],
            "error": None
        }
        with pytest.raises(ValidationError) as exc_info:
            story_service.update_story(
                "123e4567-e89b-12d3-a456-426614174000",
                {},  # Empty update data
                "user123"
            )
        assert "empty" in str(exc_info.value).lower()

    def test_get_story_progress_unauthorized(self, story_service, mock_supabase_auth):
        """Test getting story progress without authorization."""
        mock_supabase_auth.table().select().eq().execute.return_value = {
            "data": [{"user_id": "different_user"}],
            "error": None
        }
        with pytest.raises(AuthorizationError) as exc_info:
            story_service.get_story_progress(
                "123e4567-e89b-12d3-a456-426614174000",
                "user123"
            )
        assert "unauthorized" in str(exc_info.value).lower()

    def test_perform_action_story_locked(self, story_service, mock_supabase_auth):
        """Test performing an action when story is locked."""
        mock_supabase_auth.table().select().eq().execute.return_value = {
            "data": [{"state": "locked"}],
            "error": None
        }
        with pytest.raises(ValidationError) as exc_info:
            story_service.perform_action(
                "123e4567-e89b-12d3-a456-426614174000",
                "user123",
                {"action": "investigate", "target": "clue_1"}
            )
        assert "locked" in str(exc_info.value).lower()

    def test_make_choice_story_locked(self, story_service, mock_supabase_auth):
        """Test making a choice when story is locked."""
        mock_supabase_auth.table().select().eq().execute.return_value = {
            "data": [{"state": "locked", "current_choices": ["option1"]}],
            "error": None
        }
        with pytest.raises(ValidationError) as exc_info:
            story_service.make_choice(
                "123e4567-e89b-12d3-a456-426614174000",
                "user123",
                {"choice": "option1"}
            )
        assert "locked" in str(exc_info.value).lower() 