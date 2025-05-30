-- Migration script for story state schema
-- This script safely migrates data from the old stories table to the new schema

-- Start transaction
BEGIN;

-- Create temporary table to store story data
CREATE TEMPORARY TABLE temp_stories AS
SELECT 
    id,
    mystery_id,
    created_at,
    updated_at,
    current_scene,
    narrative_history,
    discovered_clues,
    suspect_states
FROM stories;

-- Create new tables
\i story_state_schema.sql

-- Migrate data to story_states
INSERT INTO story_states (
    story_id,
    created_at,
    updated_at,
    current_scene,
    narrative_history,
    player_state,
    game_progress,
    is_completed,
    version
)
SELECT 
    id,
    created_at,
    updated_at,
    current_scene,
    narrative_history,
    '{}'::JSONB, -- Default empty player state
    CASE 
        WHEN current_scene IS NOT NULL THEN 0.5 -- If there's a current scene, assume some progress
        ELSE 0.0
    END,
    FALSE, -- Default to not completed
    '1.0.0'
FROM temp_stories;

-- Migrate clues to story_clues
INSERT INTO story_clues (
    story_id,
    created_at,
    discovered_at,
    discovery_method,
    discovery_location,
    relevance_score,
    is_red_herring,
    notes,
    connections
)
SELECT 
    s.id,
    s.created_at,
    s.created_at, -- Use creation time as discovery time for existing clues
    'initial', -- Default discovery method
    'unknown', -- Default location
    0.5, -- Default relevance score
    FALSE, -- Default to not red herring
    NULL, -- No notes for migrated clues
    '[]'::JSONB -- No connections for migrated clues
FROM temp_stories s,
     jsonb_array_elements(s.discovered_clues) AS clue;

-- Migrate suspect states to story_suspects
INSERT INTO story_suspects (
    story_id,
    created_at,
    trust_level,
    suspicion_level,
    alibi_status,
    interrogation_history,
    personality_insights
)
SELECT 
    s.id,
    s.created_at,
    0.0, -- Default trust level
    0.0, -- Default suspicion level
    'unverified', -- Default alibi status
    '[]'::JSONB, -- No interrogation history
    '{}'::JSONB -- No personality insights
FROM temp_stories s,
     jsonb_each(s.suspect_states) AS suspect;

-- Create initial story actions for existing stories
INSERT INTO story_actions (
    story_id,
    created_at,
    action_type,
    content,
    result,
    success,
    difficulty_rating,
    time_taken,
    scene_location
)
SELECT 
    id,
    created_at,
    'move', -- Default action type
    jsonb_build_object('type', 'initial_setup'), -- Default content
    jsonb_build_object('status', 'success'), -- Default result
    TRUE, -- Default success
    1.0, -- Default difficulty
    0, -- No time taken
    'start' -- Default location
FROM temp_stories;

-- Create initial story choices for existing stories
INSERT INTO story_choices (
    story_id,
    created_at,
    choice_text,
    consequences,
    is_selected,
    impact_score
)
SELECT 
    id,
    created_at,
    'Begin Investigation', -- Default choice text
    jsonb_build_object('type', 'start'), -- Default consequences
    TRUE, -- Mark as selected
    0.0 -- No impact
FROM temp_stories;

-- Update story_states with last_action_time
UPDATE story_states ss
SET last_action_time = (
    SELECT MAX(created_at)
    FROM story_actions sa
    WHERE sa.story_id = ss.story_id
);

-- Drop temporary table
DROP TABLE temp_stories;

-- Commit transaction
COMMIT;

-- Verify migration
DO $$
DECLARE
    story_count INTEGER;
    state_count INTEGER;
    clue_count INTEGER;
    suspect_count INTEGER;
    action_count INTEGER;
    choice_count INTEGER;
BEGIN
    -- Get counts
    SELECT COUNT(*) INTO story_count FROM stories;
    SELECT COUNT(*) INTO state_count FROM story_states;
    SELECT COUNT(*) INTO clue_count FROM story_clues;
    SELECT COUNT(*) INTO suspect_count FROM story_suspects;
    SELECT COUNT(*) INTO action_count FROM story_actions;
    SELECT COUNT(*) INTO choice_count FROM story_choices;

    -- Verify counts match
    ASSERT story_count = state_count, 'Story count mismatch';
    ASSERT story_count = action_count, 'Action count mismatch';
    ASSERT story_count = choice_count, 'Choice count mismatch';
    
    -- Log results
    RAISE NOTICE 'Migration completed successfully:';
    RAISE NOTICE 'Stories migrated: %', story_count;
    RAISE NOTICE 'States created: %', state_count;
    RAISE NOTICE 'Clues migrated: %', clue_count;
    RAISE NOTICE 'Suspects migrated: %', suspect_count;
    RAISE NOTICE 'Actions created: %', action_count;
    RAISE NOTICE 'Choices created: %', choice_count;
END $$; 