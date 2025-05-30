import pytest
from models.template_models import Suspect, Clue, MysteryTemplate
from datetime import datetime

def test_suspect_model():
    # Test valid suspect creation
    suspect = Suspect(
        name="John Doe",
        description="A mysterious figure",
        motive="Revenge",
        alibi="Was at the library",
        guilty=False,
        personality_traits={"aggressive": 0.7, "intelligent": 0.8}
    )
    assert suspect.name == "John Doe"
    assert suspect.guilty is False
    assert suspect.personality_traits["aggressive"] == 0.7

    # Test default values
    suspect = Suspect(
        name="Jane Doe",
        description="Another suspect",
        motive="Money",
        alibi="Was at home"
    )
    assert suspect.guilty is False
    assert suspect.personality_traits == {}

def test_clue_model():
    # Test valid clue creation
    clue = Clue(
        id="clue1",
        description="A bloody knife",
        location="Kitchen",
        related_suspects=["John Doe"],
        discovery_difficulty=0.8,
        type="physical"
    )
    assert clue.id == "clue1"
    assert clue.type == "physical"
    assert clue.discovery_difficulty == 0.8

    # Test default values
    clue = Clue(
        id="clue2",
        description="A witness statement",
        location="Living room",
        type="testimony"
    )
    assert clue.related_suspects == []
    assert clue.discovery_difficulty == 1.0

    # Test invalid clue type
    with pytest.raises(ValueError):
        Clue(
            id="clue3",
            description="Invalid clue",
            location="Room",
            type="invalid_type"
        )

def test_mystery_template_model():
    # Test valid template creation
    template = MysteryTemplate(
        title="The Mansion Murder",
        description="A murder in an old mansion",
        setting="Victorian mansion",
        time_period="1920s",
        victim={"name": "Lord Blackwood", "occupation": "Nobleman"},
        suspects=[
            Suspect(
                name="John Doe",
                description="Butler",
                motive="Revenge",
                alibi="Was cleaning"
            )
        ],
        clues=[
            Clue(
                id="clue1",
                description="Bloody knife",
                location="Kitchen",
                type="physical"
            )
        ],
        red_herrings=[
            {"description": "A mysterious letter", "location": "Study"}
        ],
        difficulty=0.8,
        estimated_duration="2 hours"
    )
    assert template.title == "The Mansion Murder"
    assert template.difficulty == 0.8
    assert len(template.suspects) == 1
    assert len(template.clues) == 1
    assert len(template.red_herrings) == 1

    # Test default values
    template = MysteryTemplate(
        title="Simple Mystery",
        description="A simple mystery",
        setting="Modern apartment",
        time_period="Present",
        victim={"name": "Jane Smith", "occupation": "Writer"},
        suspects=[],
        clues=[]
    )
    assert template.difficulty == 1.0
    assert template.estimated_duration == "1 hour"
    assert template.version == "1.0.0"
    assert template.red_herrings == []

def test_mystery_template_validation():
    # Test missing required fields
    with pytest.raises(ValueError):
        MysteryTemplate(
            title="Invalid Template",
            description="Missing required fields"
        )

    # Test invalid victim format
    with pytest.raises(ValueError):
        MysteryTemplate(
            title="Invalid Template",
            description="Invalid victim format",
            setting="Modern",
            time_period="Present",
            victim="Invalid victim",  # Should be a dict
            suspects=[],
            clues=[]
        )

    # Test invalid suspects format
    with pytest.raises(ValueError):
        MysteryTemplate(
            title="Invalid Template",
            description="Invalid suspects format",
            setting="Modern",
            time_period="Present",
            victim={"name": "John", "occupation": "Writer"},
            suspects=["Invalid suspect"],  # Should be a list of Suspect objects
            clues=[]
        ) 