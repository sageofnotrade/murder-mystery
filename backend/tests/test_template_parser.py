import pytest
from backend.agents.models.template_models import MysteryTemplate, Suspect, Clue, Victim, CrimeScene, RedHerring
from backend.agents.template_agent import TemplateAgent
from unittest.mock import patch, MagicMock
import os

def sample_template():
    return MysteryTemplate(
        id="template1",
        title="The Locked Room Mystery",
        description="A classic locked-room mystery.",
        setting={"location": "Blackwood Manor", "time_period": "1930s"},
        victim=Victim(
            name="{{victim_name}}",
            description="Wealthy industrialist",
            cause_of_death="Blunt force trauma",
            found_by="{{witness_1}}"
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

def test_extract_template_variables():
    template = sample_template()
    agent = TemplateAgent(use_mem0=False)
    variables = agent.extract_template_variables(template)
    print('Extracted variables:', set(variables.keys()))
    assert set(variables.keys()) == {'alibi_1', 'motive_1', 'suspect_1', 'alibi_2', 'motive_2', 'suspect_2'}

def test_validate_template():
    template = sample_template()
    agent = TemplateAgent(use_mem0=False)
    errors = agent.validate_template(template)
    assert errors == []

    # Remove all suspects to trigger error
    template_no_suspects = template.copy(update={"suspects": []})
    errors = agent.validate_template(template_no_suspects)
    assert "Template must have at least one suspect" in errors

    # Remove all clues to trigger error
    template_no_clues = template.copy(update={"clues": []})
    errors = agent.validate_template(template_no_clues)
    assert "Template must have at least one clue" in errors

    # Remove guilty flag
    suspects = [s.copy(update={"guilty": False}) for s in template.suspects]
    template_no_guilty = template.copy(update={"suspects": suspects})
    errors = agent.validate_template(template_no_guilty)
    assert "Template must have at least one guilty suspect" in errors

def test_template_parser_functionality():
    with patch('backend.agents.template_agent.ModelRouter') as mock_router:
        mock_router.return_value.get_model_for_task.return_value = 'gpt-3.5-turbo'
        agent = TemplateAgent()
        # ... rest of the test ...

@pytest.fixture(autouse=True)
def patch_llm_model():
    with patch.dict(os.environ, {"LLM_MODEL": "gpt-3.5-turbo", "OPENAI_API_KEY": "test-key", "OPENROUTER_API_KEY": "test-key"}):
        with patch('backend.agents.template_agent.ModelRouter', MagicMock()):
            yield
