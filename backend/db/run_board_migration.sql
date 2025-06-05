-- Board State Schema Migration Runner
-- This script can be run directly in the Supabase SQL editor
-- It applies the enhanced board state schema to replace the simple boards table

-- Log the start of migration
DO $$
BEGIN
    RAISE NOTICE 'Starting board state schema migration...';
    RAISE NOTICE 'Current timestamp: %', NOW();
END $$;

-- Check if migration is needed
DO $$
DECLARE
    has_old_boards BOOLEAN := FALSE;
    has_new_schema BOOLEAN := FALSE;
BEGIN
    -- Check if old boards table exists
    SELECT EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name = 'boards'
    ) INTO has_old_boards;
    
    -- Check if new schema already exists
    SELECT EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name = 'board_states'
    ) INTO has_new_schema;
    
    IF has_new_schema THEN
        RAISE NOTICE 'New board state schema already exists. Skipping migration.';
    ELSIF has_old_boards THEN
        RAISE NOTICE 'Old boards table found. Migration needed.';
    ELSE
        RAISE NOTICE 'No existing boards table. Will create new schema.';
    END IF;
END $$;

-- Run the migration
BEGIN;

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Drop existing board-related tables if they exist
DROP TABLE IF EXISTS board_element_connections CASCADE;
DROP TABLE IF EXISTS board_connections CASCADE;
DROP TABLE IF EXISTS board_elements CASCADE;
DROP TABLE IF EXISTS board_layouts CASCADE;
DROP TABLE IF EXISTS board_notes CASCADE;
DROP TABLE IF EXISTS board_states CASCADE;

-- Create board_states table (replaces the simple boards table)
CREATE TABLE board_states (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    mystery_id UUID REFERENCES mysteries(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    name TEXT DEFAULT 'Detective Board',
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    version INTEGER DEFAULT 1,
    zoom_level FLOAT DEFAULT 1.0 CHECK (zoom_level > 0.0 AND zoom_level <= 3.0),
    pan_x FLOAT DEFAULT 0.0,
    pan_y FLOAT DEFAULT 0.0,
    grid_enabled BOOLEAN DEFAULT TRUE,
    snap_to_grid BOOLEAN DEFAULT FALSE,
    grid_size INTEGER DEFAULT 20,
    background_color TEXT DEFAULT '#f5f5f5',
    theme TEXT DEFAULT 'default' CHECK (theme IN ('default', 'dark', 'light', 'noir')),
    auto_save_enabled BOOLEAN DEFAULT TRUE,
    last_auto_save TIMESTAMP WITH TIME ZONE,
    canvas_width INTEGER DEFAULT 1200,
    canvas_height INTEGER DEFAULT 800,
    UNIQUE(mystery_id, user_id)
);

-- Create board_elements table
CREATE TABLE board_elements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    board_id UUID REFERENCES board_states(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    element_type TEXT NOT NULL CHECK (element_type IN ('suspect', 'clue', 'location', 'note', 'evidence', 'timeline', 'relationship')),
    title TEXT NOT NULL,
    description TEXT,
    content JSONB DEFAULT '{}'::JSONB,
    position_x FLOAT NOT NULL DEFAULT 0,
    position_y FLOAT NOT NULL DEFAULT 0,
    width FLOAT DEFAULT 120,
    height FLOAT DEFAULT 70,
    rotation FLOAT DEFAULT 0,
    z_index INTEGER DEFAULT 1,
    is_locked BOOLEAN DEFAULT FALSE,
    is_visible BOOLEAN DEFAULT TRUE,
    color TEXT DEFAULT '#ffffff',
    border_color TEXT DEFAULT '#dddddd',
    border_width INTEGER DEFAULT 1,
    font_size INTEGER DEFAULT 12,
    font_family TEXT DEFAULT 'Arial',
    opacity FLOAT DEFAULT 1.0 CHECK (opacity >= 0.0 AND opacity <= 1.0),
    style_properties JSONB DEFAULT '{}'::JSONB,
    metadata JSONB DEFAULT '{}'::JSONB,
    created_by_user UUID REFERENCES auth.users(id),
    last_modified_by UUID REFERENCES auth.users(id)
);

-- Create board_connections table
CREATE TABLE board_connections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    board_id UUID REFERENCES board_states(id) ON DELETE CASCADE,
    source_element_id UUID REFERENCES board_elements(id) ON DELETE CASCADE,
    target_element_id UUID REFERENCES board_elements(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    connection_type TEXT NOT NULL CHECK (connection_type IN ('thread', 'logic', 'alibi', 'evidence', 'causal', 'temporal', 'spatial', 'relationship')),
    label TEXT,
    description TEXT,
    strength FLOAT DEFAULT 1.0 CHECK (strength >= 0.0 AND strength <= 1.0),
    confidence FLOAT DEFAULT 1.0 CHECK (confidence >= 0.0 AND confidence <= 1.0),
    is_bidirectional BOOLEAN DEFAULT FALSE,
    line_style TEXT DEFAULT 'solid' CHECK (line_style IN ('solid', 'dashed', 'dotted', 'dashdot')),
    line_width INTEGER DEFAULT 2,
    line_color TEXT DEFAULT '#333333',
    arrow_style TEXT DEFAULT 'arrow' CHECK (arrow_style IN ('arrow', 'circle', 'square', 'diamond', 'none')),
    curve_type TEXT DEFAULT 'bezier' CHECK (curve_type IN ('straight', 'bezier', 'arc')),
    control_points JSONB DEFAULT '[]'::JSONB,
    is_hidden BOOLEAN DEFAULT FALSE,
    weight FLOAT DEFAULT 1.0,
    metadata JSONB DEFAULT '{}'::JSONB,
    created_by_user UUID REFERENCES auth.users(id),
    CONSTRAINT different_elements CHECK (source_element_id != target_element_id)
);

-- Create board_notes table
CREATE TABLE board_notes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    board_id UUID REFERENCES board_states(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    note_type TEXT DEFAULT 'note' CHECK (note_type IN ('note', 'annotation', 'reminder', 'question', 'hypothesis')),
    title TEXT,
    content TEXT NOT NULL,
    position_x FLOAT NOT NULL DEFAULT 0,
    position_y FLOAT NOT NULL DEFAULT 0,
    width FLOAT DEFAULT 200,
    height FLOAT DEFAULT 150,
    color TEXT DEFAULT '#ffff88',
    text_color TEXT DEFAULT '#000000',
    font_size INTEGER DEFAULT 12,
    is_pinned BOOLEAN DEFAULT FALSE,
    is_minimized BOOLEAN DEFAULT FALSE,
    attached_to_element UUID REFERENCES board_elements(id) ON DELETE SET NULL,
    priority INTEGER DEFAULT 0 CHECK (priority >= 0 AND priority <= 5),
    tags JSONB DEFAULT '[]'::JSONB,
    created_by_user UUID REFERENCES auth.users(id)
);

-- Create board_layouts table
CREATE TABLE board_layouts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    board_id UUID REFERENCES board_states(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    name TEXT NOT NULL,
    description TEXT,
    layout_type TEXT DEFAULT 'manual' CHECK (layout_type IN ('manual', 'auto_hierarchical', 'auto_circular', 'auto_force', 'timeline')),
    is_default BOOLEAN DEFAULT FALSE,
    element_positions JSONB NOT NULL DEFAULT '{}'::JSONB,
    zoom_level FLOAT DEFAULT 1.0,
    pan_x FLOAT DEFAULT 0.0,
    pan_y FLOAT DEFAULT 0.0,
    algorithm_settings JSONB DEFAULT '{}'::JSONB,
    created_by_user UUID REFERENCES auth.users(id)
);

-- Create board_element_connections junction table
CREATE TABLE board_element_connections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    element_id UUID REFERENCES board_elements(id) ON DELETE CASCADE,
    connected_element_id UUID REFERENCES board_elements(id) ON DELETE CASCADE,
    connection_id UUID REFERENCES board_connections(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    relationship_strength FLOAT DEFAULT 1.0 CHECK (relationship_strength >= 0.0 AND relationship_strength <= 1.0),
    CONSTRAINT different_connected_elements CHECK (element_id != connected_element_id),
    UNIQUE(element_id, connected_element_id, connection_id)
);

-- Create indexes for better query performance
CREATE INDEX idx_board_states_mystery_user ON board_states(mystery_id, user_id);
CREATE INDEX idx_board_states_active ON board_states(is_active);
CREATE INDEX idx_board_elements_board_id ON board_elements(board_id);
CREATE INDEX idx_board_elements_type ON board_elements(element_type);
CREATE INDEX idx_board_elements_position ON board_elements(position_x, position_y);
CREATE INDEX idx_board_elements_visible ON board_elements(is_visible);
CREATE INDEX idx_board_connections_board_id ON board_connections(board_id);
CREATE INDEX idx_board_connections_source ON board_connections(source_element_id);
CREATE INDEX idx_board_connections_target ON board_connections(target_element_id);
CREATE INDEX idx_board_connections_type ON board_connections(connection_type);
CREATE INDEX idx_board_notes_board_id ON board_notes(board_id);
CREATE INDEX idx_board_notes_attached ON board_notes(attached_to_element);
CREATE INDEX idx_board_layouts_board_id ON board_layouts(board_id);
CREATE INDEX idx_board_layouts_default ON board_layouts(is_default);

-- Enable Row Level Security
ALTER TABLE board_states ENABLE ROW LEVEL SECURITY;
ALTER TABLE board_elements ENABLE ROW LEVEL SECURITY;
ALTER TABLE board_connections ENABLE ROW LEVEL SECURITY;
ALTER TABLE board_notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE board_layouts ENABLE ROW LEVEL SECURITY;
ALTER TABLE board_element_connections ENABLE ROW LEVEL SECURITY;

-- RLS Policies for board_states
CREATE POLICY "Users can view their own board states"
    ON board_states FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own board states"
    ON board_states FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own board states"
    ON board_states FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own board states"
    ON board_states FOR DELETE
    USING (auth.uid() = user_id);

-- RLS Policies for board_elements
CREATE POLICY "Users can view elements of their boards"
    ON board_elements FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM board_states
            WHERE board_states.id = board_elements.board_id
            AND board_states.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert elements to their boards"
    ON board_elements FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM board_states
            WHERE board_states.id = board_elements.board_id
            AND board_states.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update elements of their boards"
    ON board_elements FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM board_states
            WHERE board_states.id = board_elements.board_id
            AND board_states.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete elements of their boards"
    ON board_elements FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM board_states
            WHERE board_states.id = board_elements.board_id
            AND board_states.user_id = auth.uid()
        )
    );

-- RLS Policies for board_connections
CREATE POLICY "Users can view connections of their boards"
    ON board_connections FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM board_states
            WHERE board_states.id = board_connections.board_id
            AND board_states.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert connections to their boards"
    ON board_connections FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM board_states
            WHERE board_states.id = board_connections.board_id
            AND board_states.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update connections of their boards"
    ON board_connections FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM board_states
            WHERE board_states.id = board_connections.board_id
            AND board_states.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete connections of their boards"
    ON board_connections FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM board_states
            WHERE board_states.id = board_connections.board_id
            AND board_states.user_id = auth.uid()
        )
    );

-- RLS Policies for board_notes
CREATE POLICY "Users can view notes of their boards"
    ON board_notes FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM board_states
            WHERE board_states.id = board_notes.board_id
            AND board_states.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert notes to their boards"
    ON board_notes FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM board_states
            WHERE board_states.id = board_notes.board_id
            AND board_states.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update notes of their boards"
    ON board_notes FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM board_states
            WHERE board_states.id = board_notes.board_id
            AND board_states.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete notes of their boards"
    ON board_notes FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM board_states
            WHERE board_states.id = board_notes.board_id
            AND board_states.user_id = auth.uid()
        )
    );

-- RLS Policies for board_layouts  
CREATE POLICY "Users can view layouts of their boards"
    ON board_layouts FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM board_states
            WHERE board_states.id = board_layouts.board_id
            AND board_states.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert layouts to their boards"
    ON board_layouts FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM board_states
            WHERE board_states.id = board_layouts.board_id
            AND board_states.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update layouts of their boards"
    ON board_layouts FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM board_states
            WHERE board_states.id = board_layouts.board_id
            AND board_states.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete layouts of their boards"
    ON board_layouts FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM board_states
            WHERE board_states.id = board_layouts.board_id
            AND board_states.user_id = auth.uid()
        )
    );

-- RLS Policies for board_element_connections
CREATE POLICY "Users can view element connections of their boards"
    ON board_element_connections FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM board_elements be
            JOIN board_states bs ON bs.id = be.board_id
            WHERE be.id = board_element_connections.element_id
            AND bs.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert element connections to their boards"
    ON board_element_connections FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM board_elements be
            JOIN board_states bs ON bs.id = be.board_id
            WHERE be.id = board_element_connections.element_id
            AND bs.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update element connections of their boards"
    ON board_element_connections FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM board_elements be
            JOIN board_states bs ON bs.id = be.board_id
            WHERE be.id = board_element_connections.element_id
            AND bs.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can delete element connections of their boards"
    ON board_element_connections FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM board_elements be
            JOIN board_states bs ON bs.id = be.board_id
            WHERE be.id = board_element_connections.element_id
            AND bs.user_id = auth.uid()
        )
    );

-- Create functions for automatic updated_at
CREATE OR REPLACE FUNCTION update_board_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for automatic updated_at
CREATE TRIGGER update_board_states_updated_at
BEFORE UPDATE ON board_states
FOR EACH ROW
EXECUTE FUNCTION update_board_updated_at_column();

CREATE TRIGGER update_board_elements_updated_at
BEFORE UPDATE ON board_elements
FOR EACH ROW
EXECUTE FUNCTION update_board_updated_at_column();

CREATE TRIGGER update_board_connections_updated_at
BEFORE UPDATE ON board_connections
FOR EACH ROW
EXECUTE FUNCTION update_board_updated_at_column();

CREATE TRIGGER update_board_notes_updated_at
BEFORE UPDATE ON board_notes
FOR EACH ROW
EXECUTE FUNCTION update_board_updated_at_column();

CREATE TRIGGER update_board_layouts_updated_at
BEFORE UPDATE ON board_layouts
FOR EACH ROW
EXECUTE FUNCTION update_board_updated_at_column();

-- Create function to automatically update board state when elements change
CREATE OR REPLACE FUNCTION update_board_state_on_element_change()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE board_states
    SET updated_at = NOW()
    WHERE id = COALESCE(NEW.board_id, OLD.board_id);
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Create triggers to update board state when child elements change
CREATE TRIGGER update_board_on_element_change
    AFTER INSERT OR UPDATE OR DELETE ON board_elements
    FOR EACH ROW
    EXECUTE FUNCTION update_board_state_on_element_change();

CREATE TRIGGER update_board_on_connection_change
    AFTER INSERT OR UPDATE OR DELETE ON board_connections
    FOR EACH ROW
    EXECUTE FUNCTION update_board_state_on_element_change();

CREATE TRIGGER update_board_on_note_change
    AFTER INSERT OR UPDATE OR DELETE ON board_notes
    FOR EACH ROW
    EXECUTE FUNCTION update_board_state_on_element_change();

-- Create utility functions
CREATE OR REPLACE FUNCTION get_board_statistics(board_uuid UUID)
RETURNS JSONB AS $$
DECLARE
    stats JSONB;
BEGIN
    SELECT jsonb_build_object(
        'total_elements', (
            SELECT COUNT(*) FROM board_elements 
            WHERE board_id = board_uuid AND is_visible = true
        ),
        'elements_by_type', (
            SELECT jsonb_object_agg(element_type, type_count)
            FROM (
                SELECT element_type, COUNT(*) as type_count
                FROM board_elements 
                WHERE board_id = board_uuid AND is_visible = true
                GROUP BY element_type
            ) type_counts
        ),
        'total_connections', (
            SELECT COUNT(*) FROM board_connections 
            WHERE board_id = board_uuid AND is_hidden = false
        ),
        'connections_by_type', (
            SELECT jsonb_object_agg(connection_type, type_count)
            FROM (
                SELECT connection_type, COUNT(*) as type_count
                FROM board_connections 
                WHERE board_id = board_uuid AND is_hidden = false
                GROUP BY connection_type
            ) type_counts
        ),
        'total_notes', (
            SELECT COUNT(*) FROM board_notes 
            WHERE board_id = board_uuid
        ),
        'board_complexity', (
            SELECT ROUND(
                (COUNT(DISTINCT be.id)::FLOAT + COUNT(DISTINCT bc.id)::FLOAT * 1.5) / 10, 2
            )
            FROM board_elements be
            LEFT JOIN board_connections bc ON bc.board_id = be.board_id
            WHERE be.board_id = board_uuid AND be.is_visible = true
        )
    ) INTO stats;

    RETURN stats;
END;
$$ LANGUAGE plpgsql;

-- Create function to validate board state
CREATE OR REPLACE FUNCTION validate_board_state(board_uuid UUID)
RETURNS JSONB AS $$
DECLARE
    validation_result JSONB;
    orphaned_connections INTEGER;
    overlapping_elements INTEGER;
    invalid_positions INTEGER;
BEGIN
    -- Check for orphaned connections
    SELECT COUNT(*) INTO orphaned_connections
    FROM board_connections bc
    WHERE bc.board_id = board_uuid
    AND (
        NOT EXISTS (
            SELECT 1 FROM board_elements be1 
            WHERE be1.id = bc.source_element_id AND be1.board_id = board_uuid
        )
        OR NOT EXISTS (
            SELECT 1 FROM board_elements be2 
            WHERE be2.id = bc.target_element_id AND be2.board_id = board_uuid
        )
    );

    -- Check for overlapping elements (simplified)
    SELECT COUNT(*) INTO overlapping_elements
    FROM board_elements be1
    JOIN board_elements be2 ON be1.board_id = be2.board_id 
        AND be1.id < be2.id
        AND ABS(be1.position_x - be2.position_x) < 50
        AND ABS(be1.position_y - be2.position_y) < 50
    WHERE be1.board_id = board_uuid
    AND be1.is_visible = true AND be2.is_visible = true;

    -- Check for invalid positions (outside canvas)
    SELECT COUNT(*) INTO invalid_positions
    FROM board_elements be
    JOIN board_states bs ON bs.id = be.board_id
    WHERE be.board_id = board_uuid
    AND (
        be.position_x < 0 OR be.position_y < 0 
        OR be.position_x > bs.canvas_width 
        OR be.position_y > bs.canvas_height
    );

    SELECT jsonb_build_object(
        'is_valid', (orphaned_connections = 0 AND invalid_positions = 0),
        'issues', jsonb_build_object(
            'orphaned_connections', orphaned_connections,
            'overlapping_elements', overlapping_elements,
            'invalid_positions', invalid_positions
        ),
        'warnings', CASE 
            WHEN overlapping_elements > 0 
            THEN jsonb_build_array('Some elements are overlapping')
            ELSE jsonb_build_array()
        END
    ) INTO validation_result;

    RETURN validation_result;
END;
$$ LANGUAGE plpgsql;

-- Commit the changes
COMMIT;

-- Final verification
DO $$
DECLARE
    table_count INTEGER;
    board_count INTEGER;
BEGIN
    -- Count created tables
    SELECT COUNT(*) INTO table_count
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name IN ('board_states', 'board_elements', 'board_connections', 'board_notes', 'board_layouts', 'board_element_connections');
    
    -- Count any existing boards
    SELECT COUNT(*) INTO board_count FROM board_states;
    
    RAISE NOTICE 'Board state schema migration completed successfully!';
    RAISE NOTICE 'Tables created: % of 6 expected', table_count;
    RAISE NOTICE 'Current board count: %', board_count;
    RAISE NOTICE 'Migration finished at: %', NOW();
    
    IF table_count = 6 THEN
        RAISE NOTICE '✅ All tables created successfully';
    ELSE
        RAISE WARNING '⚠️  Expected 6 tables, but only % were created', table_count;
    END IF;
END $$; 