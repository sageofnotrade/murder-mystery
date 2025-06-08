import pytest
from backend.agents.models.template_models import (
    Suspect, Clue, MysteryTemplate, Victim, CrimeScene, RedHerring
)
from pydantic import ValidationError

def test_suspect_model():
    suspect = Suspect(
        id="s1",
        name="John Doe",
        motive="Revenge",
        alibi="Was at the library",
        guilty=False,
        relationship="Butler",
        personality="Intelligent",
        secrets=["Secret1"],
        initial_suspicion=5
    )
    assert suspect.name == "John Doe"
    assert suspect.guilty is False
    assert suspect.relationship == "Butler"
    assert suspect.secrets == ["Secret1"]

    # Test default values
    suspect = Suspect(
        id="s2",
        name="Jane Doe",
        motive="Unknown",
        alibi="Unknown",
        guilty=True
    )
    assert suspect.guilty is True


def test_clue_model():
    clue = Clue(
        id="clue1",
        type="physical",
        description="A bloody knife",
        location="Kitchen",
        related_suspects=["s1"],
        discovery_difficulty="hard"
    )
    assert clue.id == "clue1"
    assert clue.type == "physical"
    assert clue.discovery_difficulty == "hard"
    assert clue.related_suspects == ["s1"]

    # Test default values
    clue = Clue(
        id="clue2",
        type="testimony",
        description="A witness statement"
    )
    assert clue.type == "testimony"
    assert clue.description == "A witness statement"


def test_mystery_template_model():
    template = MysteryTemplate(
        id="t1",
        title="The Mansion Murder",
        description="A murder in an old mansion",
        setting={"location": "Victorian mansion", "time_period": "1920s"},
        victim=Victim(
            name="Lord Blackwood",
            description="Nobleman"
        ),
        suspects=[
            Suspect(
                id="s1",
                name="John Doe",
                motive="Revenge",
                alibi="Was cleaning",
                guilty=False
            )
        ],
        clues=[
            Clue(
                id="clue1",
                type="physical",
                description="Bloody knife",
                location="Kitchen"
            )
        ],
        red_herrings=[
            RedHerring(id="r1", description="A mysterious letter", location="Study")
        ],
        difficulty="medium",
        estimated_time="2 hours"
    )
    assert template.title == "The Mansion Murder"
    assert template.difficulty == "medium"
    assert len(template.suspects) == 1
    assert len(template.clues) == 1
    assert len(template.red_herrings) == 1
    assert template.victim.name == "Lord Blackwood"
    assert template.setting["location"] == "Victorian mansion"

    # Test default values
    template = MysteryTemplate(
        id="t2",
        title="Simple Mystery",
        description="A simple mystery",
        setting={"location": "Modern apartment", "time_period": "Present"},
        victim=Victim(name="Jane Smith"),
        suspects=[],
        clues=[]
    )
    assert template.title == "Simple Mystery"
    assert template.suspects == []
    assert template.clues == []
    assert template.victim.name == "Jane Smith"


def test_mystery_template_validation():
    # Test missing required fields
    with pytest.raises(ValidationError):
        MysteryTemplate(
            description="Missing required fields"
        )

    # Test invalid victim format
    with pytest.raises(ValidationError):
        MysteryTemplate(
            title="Invalid Template",
            description="Invalid victim format",
            setting={"location": "Modern"},
            victim="Invalid victim",  # Should be a Victim object
            suspects=[],
            clues=[]
        )

    # Test invalid suspects format
    with pytest.raises(ValidationError):
        MysteryTemplate(
            title="Invalid Template",
            description="Invalid suspects format",
            setting={"location": "Modern"},
            victim=Victim(name="John"),
            suspects=["Invalid suspect"],  # Should be a list of Suspect objects
            clues=[]
        )
