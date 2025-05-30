import pytest
from models.story_models import (
    PlayerAction, NarrativeSegment, StoryChoice,
    StoryState, StoryResponse
)
from datetime import datetime
from uuid import UUID, uuid4

def test_player_action_model():
    # Test valid action creation
    action = PlayerAction(
        action_type="examine",
        content="Look at the bookshelf",
        target_id="bookshelf1"
    )
    assert action.action_type == "examine"
    assert action.content == "Look at the bookshelf"
    assert action.target_id == "bookshelf1"
    assert isinstance(action.timestamp, datetime)

    # Test default values
    action = PlayerAction(
        action_type="choice",
        content="Choose option A"
    )
    assert action.target_id is None
    assert isinstance(action.timestamp, datetime)

    # Test invalid action type
    with pytest.raises(ValueError):
        PlayerAction(
            action_type="invalid_type",
            content="Invalid action"
        )

def test_narrative_segment_model():
    # Test valid segment creation
    segment = NarrativeSegment(
        id="seg1",
        text="The detective enters the room",
        character={"name": "Detective", "role": "protagonist"}
    )
    assert segment.id == "seg1"
    assert segment.text == "The detective enters the room"
    assert segment.character["name"] == "Detective"
    assert isinstance(segment.timestamp, datetime)

    # Test default values
    segment = NarrativeSegment(
        id="seg2",
        text="A simple narrative segment"
    )
    assert segment.character is None
    assert isinstance(segment.timestamp, datetime)

def test_story_choice_model():
    # Test valid choice creation
    choice = StoryChoice(
        id="choice1",
        text="Examine the desk",
        consequences="You find a hidden compartment"
    )
    assert choice.id == "choice1"
    assert choice.text == "Examine the desk"
    assert choice.consequences == "You find a hidden compartment"

    # Test default values
    choice = StoryChoice(
        id="choice2",
        text="Leave the room"
    )
    assert choice.consequences is None

def test_story_state_model():
    # Test valid state creation
    mystery_id = uuid4()
    state = StoryState(
        id=uuid4(),
        mystery_id=mystery_id,
        current_scene="library",
        narrative_history=[
            NarrativeSegment(
                id="seg1",
                text="The detective enters the library"
            )
        ],
        discovered_clues=[
            {"id": "clue1", "description": "A bloody knife"}
        ],
        suspect_states={
            "suspect1": {"suspicious": True, "alibi": "Was at home"}
        },
        player_choices=[
            StoryChoice(id="choice1", text="Examine the desk")
        ],
        last_action=PlayerAction(
            action_type="examine",
            content="Look at the desk"
        )
    )
    assert isinstance(state.id, UUID)
    assert state.mystery_id == mystery_id
    assert state.current_scene == "library"
    assert len(state.narrative_history) == 1
    assert len(state.discovered_clues) == 1
    assert len(state.suspect_states) == 1
    assert len(state.player_choices) == 1
    assert isinstance(state.created_at, datetime)
    assert isinstance(state.updated_at, datetime)

    # Test default values
    state = StoryState(
        mystery_id=uuid4(),
        current_scene="entrance"
    )
    assert state.narrative_history == []
    assert state.discovered_clues == []
    assert state.suspect_states == {}
    assert state.player_choices == []
    assert state.last_action is None

def test_story_response_model():
    # Test valid response creation
    story_id = uuid4()
    response = StoryResponse(
        story_id=story_id,
        narrative="The detective finds a clue",
        choices=[
            StoryChoice(id="choice1", text="Examine the clue"),
            StoryChoice(id="choice2", text="Leave it alone")
        ],
        discovered_clues=[
            {"id": "clue1", "description": "A mysterious note"}
        ],
        suspect_states={
            "suspect1": {"suspicious": True}
        },
        current_scene="study"
    )
    assert response.story_id == story_id
    assert response.narrative == "The detective finds a clue"
    assert len(response.choices) == 2
    assert len(response.discovered_clues) == 1
    assert len(response.suspect_states) == 1
    assert response.current_scene == "study"
    assert isinstance(response.timestamp, datetime)

def test_story_state_validation():
    # Test missing required fields
    with pytest.raises(ValueError):
        StoryState(
            current_scene="library"  # Missing mystery_id
        )

    # Test invalid UUID format
    with pytest.raises(ValueError):
        StoryState(
            mystery_id="invalid-uuid",
            current_scene="library"
        )

    # Test invalid narrative history format
    with pytest.raises(ValueError):
        StoryState(
            mystery_id=uuid4(),
            current_scene="library",
            narrative_history=["Invalid segment"]  # Should be a list of NarrativeSegment objects
        ) 