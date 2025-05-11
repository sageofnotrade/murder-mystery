-- Supabase SQL schema for Murþrą

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create profiles table
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    psychological_traits JSONB DEFAULT '{}'::JSONB,
    preferences JSONB DEFAULT '{}'::JSONB,
    play_history JSONB DEFAULT '{}'::JSONB,
    UNIQUE(user_id)
);

-- Create RLS policies for profiles
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own profile"
    ON profiles FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can update their own profile"
    ON profiles FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own profile"
    ON profiles FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Create mystery_templates table
CREATE TABLE IF NOT EXISTS mystery_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    title TEXT NOT NULL,
    description TEXT,
    difficulty TEXT CHECK (difficulty IN ('easy', 'medium', 'hard')),
    structure JSONB NOT NULL,
    is_public BOOLEAN DEFAULT FALSE
);

-- Create mysteries table
CREATE TABLE IF NOT EXISTS mysteries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    template_id UUID REFERENCES mystery_templates(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    title TEXT NOT NULL,
    state JSONB DEFAULT '{}'::JSONB,
    is_completed BOOLEAN DEFAULT FALSE
);

-- Create RLS policies for mysteries
ALTER TABLE mysteries ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own mysteries"
    ON mysteries FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can update their own mysteries"
    ON mysteries FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own mysteries"
    ON mysteries FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Create stories table
CREATE TABLE IF NOT EXISTS stories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    mystery_id UUID REFERENCES mysteries(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    current_scene TEXT,
    narrative_history JSONB DEFAULT '[]'::JSONB,
    discovered_clues JSONB DEFAULT '[]'::JSONB,
    suspect_states JSONB DEFAULT '{}'::JSONB
);

-- Create RLS policies for stories
ALTER TABLE stories ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own stories"
    ON stories FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM mysteries
            WHERE mysteries.id = stories.mystery_id
            AND mysteries.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update their own stories"
    ON stories FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM mysteries
            WHERE mysteries.id = stories.mystery_id
            AND mysteries.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert their own stories"
    ON stories FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM mysteries
            WHERE mysteries.id = stories.mystery_id
            AND mysteries.user_id = auth.uid()
        )
    );

-- Create boards table
CREATE TABLE IF NOT EXISTS boards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    mystery_id UUID REFERENCES mysteries(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    elements JSONB DEFAULT '[]'::JSONB,
    connections JSONB DEFAULT '[]'::JSONB,
    notes JSONB DEFAULT '[]'::JSONB,
    layout JSONB DEFAULT '{}'::JSONB
);

-- Create RLS policies for boards
ALTER TABLE boards ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own boards"
    ON boards FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM mysteries
            WHERE mysteries.id = boards.mystery_id
            AND mysteries.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update their own boards"
    ON boards FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM mysteries
            WHERE mysteries.id = boards.mystery_id
            AND mysteries.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert their own boards"
    ON boards FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM mysteries
            WHERE mysteries.id = boards.mystery_id
            AND mysteries.user_id = auth.uid()
        )
    );

-- Create functions for automatic updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for automatic updated_at
CREATE TRIGGER update_profiles_updated_at
BEFORE UPDATE ON profiles
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_mystery_templates_updated_at
BEFORE UPDATE ON mystery_templates
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_mysteries_updated_at
BEFORE UPDATE ON mysteries
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_stories_updated_at
BEFORE UPDATE ON stories
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_boards_updated_at
BEFORE UPDATE ON boards
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();
