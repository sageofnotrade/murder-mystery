import pytest
from backend.agents.models.template_models import (
    MysteryTemplate, Suspect, Clue, Victim, CrimeScene, RedHerring
)
from backend.agents.models.player_models import PlayerProfile
from backend.agents.template_agent import TemplateAgent

def sample_template():
    return MysteryTemplate(
        id="template1",
        title="The Locked Room Mystery",
        description="A classic locked-room mystery.",
        difficulty="medium",
        estimated_time="60-90 minutes",
        player_role="detective",
        psychological_profile_weights={"analytical": 0.8, "intuitive": 0.6},
        setting={"location": "Blackwood Manor", "time_period": "1930s"},
        victim=Victim(
            name="{{victim_name}}",
            description="Wealthy industrialist",
            cause_of_death="Blunt force trauma",
            time_of_death="Between 10 PM and midnight",
            found_by="{{witness_1}}",
            background="Known for ruthless business practices"
        ),
        crime_scene=CrimeScene(
            location="Study on the second floor",
            locked_from="inside",
            entry_points=["Door (locked from inside)", "Window (sealed)"]
        ),
        suspects=[
            Suspect(id="s1", name="{{suspect_1}}", motive="{{motive_1}}", alibi="{{alibi_1}}", guilty=True),
            Suspect(id="s2", name="{{suspect_2}}", motive="{{motive_2}}", alibi="{{alibi_2}}", guilty=False),
        ],
        clues=[
            Clue(id="c1", type="physical", description="A bloodied candlestick", location="bookshelf", relevance="murder weapon", related_suspects=["s1"]),
            Clue(id="c2", type="logical", description="The window was unlocked from the outside", location=None, relevance="explains the locked-room trick", related_suspects=[]),
        ],
        red_herrings=[
            RedHerring(id="r1", description="A torn photo suggesting an affair (unrelated)", location="desk", misleading_conclusion="Affair motive", actual_explanation="Unrelated photo")
        ]
    )

@pytest.fixture
def sample_player_profile():
    return PlayerProfile(
        psychological_traits={"logic": 0.8, "intuition": 0.6},
        preferences={"setting": "classic", "difficulty": "medium"},
        play_history={}
    )

def test_populate_template(sample_player_profile):
    template = sample_template()
    agent = TemplateAgent(use_mem0=False)
    populated = agent.populate_template(template, sample_player_profile)
    # All variables should be replaced with generated values
    assert "{{" not in populated.victim.name
    for suspect in populated.suspects:
        assert "{{" not in suspect.name
        assert "{{" not in suspect.motive
        assert "{{" not in suspect.alibi
    # Check nested fields
    assert populated.victim.name != "{{victim_name}}"
    assert populated.victim.found_by != "{{witness_1}}"
