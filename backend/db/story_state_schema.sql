-- Enhanced story state schema for Murþrą

-- Drop existing story-related tables if they exist
DROP TABLE IF EXISTS story_states CASCADE;
DROP TABLE IF EXISTS story_actions CASCADE;
DROP TABLE IF EXISTS story_choices CASCADE;
DROP TABLE IF EXISTS story_clues CASCADE;
DROP TABLE IF EXISTS story_suspects CASCADE;

-- Create story_states table (enhanced version of stories table)
CREATE TABLE story_states (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    story_id UUID REFERENCES stories(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    current_scene TEXT NOT NULL,
    narrative_history JSONB DEFAULT '[]'::JSONB,
    player_state JSONB DEFAULT '{}'::JSONB,
    game_progress FLOAT DEFAULT 0.0 CHECK (game_progress >= 0.0 AND game_progress <= 1.0),
    is_completed BOOLEAN DEFAULT FALSE,
    completion_time TIMESTAMP WITH TIME ZONE,
    difficulty_multiplier FLOAT DEFAULT 1.0 CHECK (difficulty_multiplier > 0.0),
    version TEXT NOT NULL DEFAULT '1.0.0',
    last_action_time TIMESTAMP WITH TIME ZONE,
    total_play_time INTEGER DEFAULT 0 -- in seconds
);

-- Create story_actions table
CREATE TABLE story_actions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    story_id UUID REFERENCES stories(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    action_type TEXT NOT NULL CHECK (action_type IN ('investigate', 'interrogate', 'examine', 'move', 'deduce')),
    content JSONB NOT NULL,
    result JSONB NOT NULL,
    success BOOLEAN NOT NULL,
    difficulty_rating FLOAT DEFAULT 1.0 CHECK (difficulty_rating > 0.0),
    time_taken INTEGER DEFAULT 0, -- in seconds
    scene_location TEXT NOT NULL
);

-- Create story_choices table
CREATE TABLE story_choices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    story_id UUID REFERENCES stories(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    choice_text TEXT NOT NULL,
    consequences JSONB NOT NULL,
    is_selected BOOLEAN DEFAULT FALSE,
    selection_time TIMESTAMP WITH TIME ZONE,
    impact_score FLOAT DEFAULT 0.0 CHECK (impact_score >= -1.0 AND impact_score <= 1.0)
);

-- Create story_clues table
CREATE TABLE story_clues (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    story_id UUID REFERENCES stories(id) ON DELETE CASCADE,
    template_clue_id UUID REFERENCES template_clues(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    discovered_at TIMESTAMP WITH TIME ZONE,
    discovery_method TEXT NOT NULL,
    discovery_location TEXT NOT NULL,
    relevance_score FLOAT DEFAULT 0.0 CHECK (relevance_score >= 0.0 AND relevance_score <= 1.0),
    is_red_herring BOOLEAN DEFAULT FALSE,
    notes TEXT,
    connections JSONB DEFAULT '[]'::JSONB
);

-- Create story_suspects table
CREATE TABLE story_suspects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    story_id UUID REFERENCES stories(id) ON DELETE CASCADE,
    template_suspect_id UUID REFERENCES template_suspects(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    trust_level FLOAT DEFAULT 0.0 CHECK (trust_level >= -1.0 AND trust_level <= 1.0),
    suspicion_level FLOAT DEFAULT 0.0 CHECK (suspicion_level >= 0.0 AND suspicion_level <= 1.0),
    alibi_status TEXT CHECK (alibi_status IN ('verified', 'unverified', 'contradicted')),
    interrogation_history JSONB DEFAULT '[]'::JSONB,
    personality_insights JSONB DEFAULT '{}'::JSONB
);

-- Enable Row Level Security
ALTER TABLE story_states ENABLE ROW LEVEL SECURITY;
ALTER TABLE story_actions ENABLE ROW LEVEL SECURITY;
ALTER TABLE story_choices ENABLE ROW LEVEL SECURITY;
ALTER TABLE story_clues ENABLE ROW LEVEL SECURITY;
ALTER TABLE story_suspects ENABLE ROW LEVEL SECURITY;

-- RLS Policies for story_states
CREATE POLICY "Users can view their own story states"
    ON story_states FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM stories
            JOIN mysteries ON stories.mystery_id = mysteries.id
            WHERE stories.id = story_states.story_id
            AND mysteries.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update their own story states"
    ON story_states FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM stories
            JOIN mysteries ON stories.mystery_id = mysteries.id
            WHERE stories.id = story_states.story_id
            AND mysteries.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert their own story states"
    ON story_states FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM stories
            JOIN mysteries ON stories.mystery_id = mysteries.id
            WHERE stories.id = story_states.story_id
            AND mysteries.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete their own story states"
    ON story_states FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM stories
            JOIN mysteries ON stories.mystery_id = mysteries.id
            WHERE stories.id = story_states.story_id
            AND mysteries.user_id = auth.uid()
        )
    );

-- RLS Policies for story_actions
CREATE POLICY "Users can view their own story actions"
    ON story_actions FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM stories
            JOIN mysteries ON stories.mystery_id = mysteries.id
            WHERE stories.id = story_actions.story_id
            AND mysteries.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert their own story actions"
    ON story_actions FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM stories
            JOIN mysteries ON stories.mystery_id = mysteries.id
            WHERE stories.id = story_actions.story_id
            AND mysteries.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update their own story actions"
    ON story_actions FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM stories
            JOIN mysteries ON stories.mystery_id = mysteries.id
            WHERE stories.id = story_actions.story_id
            AND mysteries.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete their own story actions"
    ON story_actions FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM stories
            JOIN mysteries ON stories.mystery_id = mysteries.id
            WHERE stories.id = story_actions.story_id
            AND mysteries.user_id = auth.uid()
        )
    );

-- RLS Policies for story_choices
CREATE POLICY "Users can view their own story choices"
    ON story_choices FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM stories
            JOIN mysteries ON stories.mystery_id = mysteries.id
            WHERE stories.id = story_choices.story_id
            AND mysteries.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update their own story choices"
    ON story_choices FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM stories
            JOIN mysteries ON stories.mystery_id = mysteries.id
            WHERE stories.id = story_choices.story_id
            AND mysteries.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert their own story choices"
    ON story_choices FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM stories
            JOIN mysteries ON stories.mystery_id = mysteries.id
            WHERE stories.id = story_choices.story_id
            AND mysteries.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete their own story choices"
    ON story_choices FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM stories
            JOIN mysteries ON stories.mystery_id = mysteries.id
            WHERE stories.id = story_choices.story_id
            AND mysteries.user_id = auth.uid()
        )
    );

-- RLS Policies for story_clues
CREATE POLICY "Users can view their own story clues"
    ON story_clues FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM stories
            JOIN mysteries ON stories.mystery_id = mysteries.id
            WHERE stories.id = story_clues.story_id
            AND mysteries.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update their own story clues"
    ON story_clues FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM stories
            JOIN mysteries ON stories.mystery_id = mysteries.id
            WHERE stories.id = story_clues.story_id
            AND mysteries.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert their own story clues"
    ON story_clues FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM stories
            JOIN mysteries ON stories.mystery_id = mysteries.id
            WHERE stories.id = story_clues.story_id
            AND mysteries.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete their own story clues"
    ON story_clues FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM stories
            JOIN mysteries ON stories.mystery_id = mysteries.id
            WHERE stories.id = story_clues.story_id
            AND mysteries.user_id = auth.uid()
        )
    );

-- RLS Policies for story_suspects
CREATE POLICY "Users can view their own story suspects"
    ON story_suspects FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM stories
            JOIN mysteries ON stories.mystery_id = mysteries.id
            WHERE stories.id = story_suspects.story_id
            AND mysteries.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update their own story suspects"
    ON story_suspects FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM stories
            JOIN mysteries ON stories.mystery_id = mysteries.id
            WHERE stories.id = story_suspects.story_id
            AND mysteries.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert their own story suspects"
    ON story_suspects FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM stories
            JOIN mysteries ON stories.mystery_id = mysteries.id
            WHERE stories.id = story_suspects.story_id
            AND mysteries.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete their own story suspects"
    ON story_suspects FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM stories
            JOIN mysteries ON stories.mystery_id = mysteries.id
            WHERE stories.id = story_suspects.story_id
            AND mysteries.user_id = auth.uid()
        )
    );

-- Create indexes for better query performance
CREATE INDEX idx_story_states_story_id ON story_states(story_id);
CREATE INDEX idx_story_actions_story_id ON story_actions(story_id);
CREATE INDEX idx_story_choices_story_id ON story_choices(story_id);
CREATE INDEX idx_story_clues_story_id ON story_clues(story_id);
CREATE INDEX idx_story_suspects_story_id ON story_suspects(story_id);
CREATE INDEX idx_story_clues_template_clue_id ON story_clues(template_clue_id);
CREATE INDEX idx_story_suspects_template_suspect_id ON story_suspects(template_suspect_id);
CREATE INDEX idx_story_actions_action_type ON story_actions(action_type);
CREATE INDEX idx_story_clues_discovered_at ON story_clues(discovered_at);
CREATE INDEX idx_story_choices_is_selected ON story_choices(is_selected);
CREATE INDEX idx_story_suspects_alibi_status ON story_suspects(alibi_status);

-- Create triggers for automatic updated_at
CREATE TRIGGER update_story_states_updated_at
    BEFORE UPDATE ON story_states
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_story_actions_updated_at
    BEFORE UPDATE ON story_actions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_story_choices_updated_at
    BEFORE UPDATE ON story_choices
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_story_clues_updated_at
    BEFORE UPDATE ON story_clues
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_story_suspects_updated_at
    BEFORE UPDATE ON story_suspects
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column(); 