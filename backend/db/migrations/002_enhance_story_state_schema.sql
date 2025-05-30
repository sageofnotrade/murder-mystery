-- Migration script to enhance story state schema
-- This script adds new features and optimizations to the story state schema

-- Start transaction
BEGIN;

-- Add new columns to story_states table
ALTER TABLE story_states
ADD COLUMN IF NOT EXISTS difficulty_level TEXT CHECK (difficulty_level IN ('easy', 'medium', 'hard')),
ADD COLUMN IF NOT EXISTS player_profile JSONB DEFAULT '{}'::JSONB,
ADD COLUMN IF NOT EXISTS achievement_progress JSONB DEFAULT '{}'::JSONB,
ADD COLUMN IF NOT EXISTS game_settings JSONB DEFAULT '{}'::JSONB,
ADD COLUMN IF NOT EXISTS last_save_point JSONB DEFAULT '{}'::JSONB;

-- Add new columns to story_actions table
ALTER TABLE story_actions
ADD COLUMN IF NOT EXISTS player_skill_level FLOAT DEFAULT 1.0,
ADD COLUMN IF NOT EXISTS difficulty_multiplier FLOAT DEFAULT 1.0,
ADD COLUMN IF NOT EXISTS success_probability FLOAT DEFAULT 1.0,
ADD COLUMN IF NOT EXISTS actual_difficulty FLOAT GENERATED ALWAYS AS (difficulty_rating * difficulty_multiplier) STORED;

-- Add new columns to story_choices table
ALTER TABLE story_choices
ADD COLUMN IF NOT EXISTS difficulty_level TEXT CHECK (difficulty_level IN ('easy', 'medium', 'hard')),
ADD COLUMN IF NOT EXISTS required_skills JSONB DEFAULT '[]'::JSONB,
ADD COLUMN IF NOT EXISTS skill_impact JSONB DEFAULT '{}'::JSONB;

-- Add new columns to story_suspects table
ALTER TABLE story_suspects
ADD COLUMN IF NOT EXISTS relationship_level FLOAT DEFAULT 0.0 CHECK (relationship_level >= -1.0 AND relationship_level <= 1.0),
ADD COLUMN IF NOT EXISTS known_secrets JSONB DEFAULT '[]'::JSONB,
ADD COLUMN IF NOT EXISTS interaction_history JSONB DEFAULT '[]'::JSONB;

-- Create new indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_story_states_difficulty ON story_states(difficulty_level);
CREATE INDEX IF NOT EXISTS idx_story_actions_difficulty ON story_actions(actual_difficulty);
CREATE INDEX IF NOT EXISTS idx_story_choices_difficulty ON story_choices(difficulty_level);
CREATE INDEX IF NOT EXISTS idx_story_suspects_relationship ON story_suspects(relationship_level);

-- Create new functions for story state management
CREATE OR REPLACE FUNCTION calculate_story_progress(story_id UUID)
RETURNS FLOAT AS $$
DECLARE
    total_actions INTEGER;
    completed_actions INTEGER;
    total_clues INTEGER;
    discovered_clues INTEGER;
    total_suspects INTEGER;
    interrogated_suspects INTEGER;
BEGIN
    -- Calculate progress based on actions
    SELECT COUNT(*) INTO total_actions
    FROM story_actions
    WHERE story_id = $1;

    SELECT COUNT(*) INTO completed_actions
    FROM story_actions
    WHERE story_id = $1 AND success = true;

    -- Calculate progress based on clues
    SELECT COUNT(*) INTO total_clues
    FROM story_clues sc
    JOIN stories s ON s.id = sc.story_id
    JOIN mysteries m ON m.id = s.mystery_id
    JOIN mystery_templates mt ON mt.id = m.template_id
    JOIN template_clues tc ON tc.template_id = mt.id
    WHERE s.id = $1;

    SELECT COUNT(*) INTO discovered_clues
    FROM story_clues
    WHERE story_id = $1;

    -- Calculate progress based on suspects
    SELECT COUNT(*) INTO total_suspects
    FROM story_suspects ss
    JOIN stories s ON s.id = ss.story_id
    JOIN mysteries m ON m.id = s.mystery_id
    JOIN mystery_templates mt ON mt.id = m.template_id
    JOIN template_suspects ts ON ts.template_id = mt.id
    WHERE s.id = $1;

    SELECT COUNT(*) INTO interrogated_suspects
    FROM story_suspects
    WHERE story_id = $1 AND jsonb_array_length(interrogation_history) > 0;

    -- Calculate overall progress (weighted average)
    RETURN (
        (completed_actions::FLOAT / NULLIF(total_actions, 0) * 0.4) +
        (discovered_clues::FLOAT / NULLIF(total_clues, 0) * 0.4) +
        (interrogated_suspects::FLOAT / NULLIF(total_suspects, 0) * 0.2)
    );
END;
$$ LANGUAGE plpgsql;

-- Create trigger to update game progress
CREATE OR REPLACE FUNCTION update_story_progress()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE story_states
    SET game_progress = calculate_story_progress(story_id)
    WHERE story_id = NEW.story_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_progress_after_action
    AFTER INSERT OR UPDATE ON story_actions
    FOR EACH ROW
    EXECUTE FUNCTION update_story_progress();

CREATE TRIGGER update_progress_after_clue
    AFTER INSERT OR UPDATE ON story_clues
    FOR EACH ROW
    EXECUTE FUNCTION update_story_progress();

CREATE TRIGGER update_progress_after_suspect
    AFTER INSERT OR UPDATE ON story_suspects
    FOR EACH ROW
    EXECUTE FUNCTION update_story_progress();

-- Create function to get story statistics
CREATE OR REPLACE FUNCTION get_story_statistics(story_id UUID)
RETURNS JSONB AS $$
DECLARE
    stats JSONB;
BEGIN
    SELECT jsonb_build_object(
        'total_actions', COUNT(*),
        'successful_actions', COUNT(*) FILTER (WHERE success = true),
        'average_difficulty', AVG(actual_difficulty),
        'total_play_time', SUM(time_taken)
    ) INTO stats
    FROM story_actions
    WHERE story_id = $1;

    RETURN stats;
END;
$$ LANGUAGE plpgsql;

-- Commit transaction
COMMIT;

-- Verify migration
DO $$
DECLARE
    story_count INTEGER;
    action_count INTEGER;
    clue_count INTEGER;
    suspect_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO story_count FROM story_states;
    SELECT COUNT(*) INTO action_count FROM story_actions;
    SELECT COUNT(*) INTO clue_count FROM story_clues;
    SELECT COUNT(*) INTO suspect_count FROM story_suspects;

    RAISE NOTICE 'Migration completed successfully. Current counts:';
    RAISE NOTICE 'Stories: %', story_count;
    RAISE NOTICE 'Actions: %', action_count;
    RAISE NOTICE 'Clues: %', clue_count;
    RAISE NOTICE 'Suspects: %', suspect_count;
END $$; 