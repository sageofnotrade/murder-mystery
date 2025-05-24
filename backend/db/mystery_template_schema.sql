-- Enhanced mystery template schema for Murþrą

-- Drop existing mystery_templates table if it exists
DROP TABLE IF EXISTS mystery_templates CASCADE;

-- Create enhanced mystery templates table
CREATE TABLE mystery_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    setting TEXT NOT NULL,
    time_period TEXT NOT NULL,
    difficulty FLOAT NOT NULL DEFAULT 1.0,
    estimated_duration TEXT NOT NULL DEFAULT '1 hour',
    version TEXT NOT NULL DEFAULT '1.0.0',
    is_published BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id)
);

-- Create victims table
CREATE TABLE template_victims (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    template_id UUID REFERENCES mystery_templates(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    background TEXT NOT NULL,
    cause_of_death TEXT NOT NULL,
    discovery_details TEXT NOT NULL
);

-- Create suspects table
CREATE TABLE template_suspects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    template_id UUID REFERENCES mystery_templates(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    background TEXT NOT NULL,
    motive TEXT NOT NULL,
    alibi TEXT NOT NULL,
    is_guilty BOOLEAN NOT NULL DEFAULT FALSE,
    personality_traits JSONB NOT NULL DEFAULT '{}'::JSONB
);

-- Create clues table
CREATE TABLE template_clues (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    template_id UUID REFERENCES mystery_templates(id) ON DELETE CASCADE,
    description TEXT NOT NULL,
    location TEXT NOT NULL,
    discovery_difficulty FLOAT NOT NULL DEFAULT 1.0,
    clue_type TEXT NOT NULL CHECK (clue_type IN ('physical', 'testimony', 'observation', 'document')),
    related_suspects JSONB NOT NULL DEFAULT '[]'::JSONB,
    is_red_herring BOOLEAN NOT NULL DEFAULT FALSE
);

-- Create locations table
CREATE TABLE template_locations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    template_id UUID REFERENCES mystery_templates(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    significance TEXT NOT NULL
);

-- Enable Row Level Security
ALTER TABLE mystery_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE template_victims ENABLE ROW LEVEL SECURITY;
ALTER TABLE template_suspects ENABLE ROW LEVEL SECURITY;
ALTER TABLE template_clues ENABLE ROW LEVEL SECURITY;
ALTER TABLE template_locations ENABLE ROW LEVEL SECURITY;

-- RLS Policies for mystery_templates
CREATE POLICY "Anyone can read published templates"
    ON mystery_templates FOR SELECT
    USING (is_published = TRUE);

CREATE POLICY "Creators can do anything with their templates"
    ON mystery_templates FOR ALL
    USING (auth.uid() = created_by);

-- RLS Policies for template_victims
CREATE POLICY "Anyone can read victims of published templates"
    ON template_victims FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM mystery_templates
            WHERE mystery_templates.id = template_victims.template_id
            AND mystery_templates.is_published = TRUE
        )
    );

CREATE POLICY "Creators can manage victims of their templates"
    ON template_victims FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM mystery_templates
            WHERE mystery_templates.id = template_victims.template_id
            AND mystery_templates.created_by = auth.uid()
        )
    );

-- RLS Policies for template_suspects
CREATE POLICY "Anyone can read suspects of published templates"
    ON template_suspects FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM mystery_templates
            WHERE mystery_templates.id = template_suspects.template_id
            AND mystery_templates.is_published = TRUE
        )
    );

CREATE POLICY "Creators can manage suspects of their templates"
    ON template_suspects FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM mystery_templates
            WHERE mystery_templates.id = template_suspects.template_id
            AND mystery_templates.created_by = auth.uid()
        )
    );

-- RLS Policies for template_clues
CREATE POLICY "Anyone can read clues of published templates"
    ON template_clues FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM mystery_templates
            WHERE mystery_templates.id = template_clues.template_id
            AND mystery_templates.is_published = TRUE
        )
    );

CREATE POLICY "Creators can manage clues of their templates"
    ON template_clues FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM mystery_templates
            WHERE mystery_templates.id = template_clues.template_id
            AND mystery_templates.created_by = auth.uid()
        )
    );

-- RLS Policies for template_locations
CREATE POLICY "Anyone can read locations of published templates"
    ON template_locations FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM mystery_templates
            WHERE mystery_templates.id = template_locations.template_id
            AND mystery_templates.is_published = TRUE
        )
    );

CREATE POLICY "Creators can manage locations of their templates"
    ON template_locations FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM mystery_templates
            WHERE mystery_templates.id = template_locations.template_id
            AND mystery_templates.created_by = auth.uid()
        )
    );

-- Create trigger for updated_at on mystery_templates
CREATE TRIGGER update_mystery_templates_updated_at
    BEFORE UPDATE ON mystery_templates
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column(); 