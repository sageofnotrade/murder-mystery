-- Rollback script for board state migration
-- This script safely reverts the enhanced board state schema back to the original boards table

-- Start transaction
BEGIN;

-- Create the original boards table structure
CREATE TABLE IF NOT EXISTS boards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    mystery_id UUID REFERENCES mysteries(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    elements JSONB DEFAULT '[]'::JSONB,
    connections JSONB DEFAULT '[]'::JSONB,
    notes JSONB DEFAULT '{}'::JSONB,
    layout JSONB DEFAULT '{}'::JSONB
);

-- Enable RLS for original boards table
ALTER TABLE boards ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for original boards table
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

-- Create trigger for automatic updated_at
CREATE TRIGGER update_boards_updated_at
BEFORE UPDATE ON boards
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Migrate data back from new schema to original boards table
INSERT INTO boards (
    id,
    mystery_id,
    created_at,
    updated_at,
    elements,
    connections,
    notes,
    layout
)
SELECT 
    bs.id,
    bs.mystery_id,
    bs.created_at,
    bs.updated_at,
    -- Reconstruct elements JSONB array
    COALESCE(
        (SELECT jsonb_agg(
            jsonb_build_object(
                'id', be.id,
                'type', be.element_type,
                'title', be.title,
                'name', be.title, -- Include legacy name field
                'description', be.description,
                'position', jsonb_build_object('x', be.position_x, 'y', be.position_y),
                'properties', be.content,
                'content', be.content, -- Include legacy content field
                'width', be.width,
                'height', be.height,
                'rotation', be.rotation,
                'z_index', be.z_index,
                'locked', be.is_locked,
                'visible', be.is_visible,
                'color', be.color,
                'border_color', be.border_color,
                'border_width', be.border_width,
                'font_size', be.font_size,
                'font_family', be.font_family,
                'opacity', be.opacity,
                'style', be.style_properties,
                'metadata', be.metadata
            )
        )
        FROM board_elements be 
        WHERE be.board_id = bs.id),
        '[]'::JSONB
    ) AS elements,
    -- Reconstruct connections JSONB array
    COALESCE(
        (SELECT jsonb_agg(
            jsonb_build_object(
                'id', bc.id,
                'sourceId', bc.source_element_id,
                'targetId', bc.target_element_id,
                'source_id', bc.source_element_id, -- Include legacy field name
                'target_id', bc.target_element_id, -- Include legacy field name
                'type', bc.connection_type,
                'label', bc.label,
                'description', bc.description,
                'strength', bc.strength,
                'confidence', bc.confidence,
                'bidirectional', bc.is_bidirectional,
                'line_style', bc.line_style,
                'line_width', bc.line_width,
                'line_color', bc.line_color,
                'arrow_style', bc.arrow_style,
                'curve_type', bc.curve_type,
                'control_points', bc.control_points,
                'hidden', bc.is_hidden,
                'weight', bc.weight,
                'metadata', bc.metadata
            )
        )
        FROM board_connections bc 
        WHERE bc.board_id = bs.id),
        '[]'::JSONB
    ) AS connections,
    -- Reconstruct notes JSONB object
    COALESCE(
        (SELECT jsonb_object_agg(
            bn.id::TEXT,
            jsonb_build_object(
                'id', bn.id,
                'type', bn.note_type,
                'title', bn.title,
                'content', bn.content,
                'text', bn.content, -- Include legacy text field
                'position', jsonb_build_object('x', bn.position_x, 'y', bn.position_y),
                'width', bn.width,
                'height', bn.height,
                'color', bn.color,
                'text_color', bn.text_color,
                'font_size', bn.font_size,
                'pinned', bn.is_pinned,
                'minimized', bn.is_minimized,
                'priority', bn.priority,
                'tags', bn.tags
            )
        )
        FROM board_notes bn 
        WHERE bn.board_id = bs.id),
        '{}'::JSONB
    ) AS notes,
    -- Reconstruct layout JSONB object
    jsonb_build_object(
        'zoom', bs.zoom_level,
        'pan_x', bs.pan_x,
        'pan_y', bs.pan_y,
        'grid_enabled', bs.grid_enabled,
        'snap_to_grid', bs.snap_to_grid,
        'grid_size', bs.grid_size,
        'background_color', bs.background_color,
        'theme', bs.theme,
        'canvas_width', bs.canvas_width,
        'canvas_height', bs.canvas_height
    ) AS layout
FROM board_states bs;

-- Drop the new schema tables in reverse dependency order
DROP TABLE IF EXISTS board_element_connections CASCADE;
DROP TABLE IF EXISTS board_connections CASCADE;
DROP TABLE IF EXISTS board_elements CASCADE;
DROP TABLE IF EXISTS board_layouts CASCADE;
DROP TABLE IF EXISTS board_notes CASCADE;
DROP TABLE IF EXISTS board_states CASCADE;

-- Drop the legacy view if it exists
DROP VIEW IF EXISTS legacy_boards CASCADE;

-- Drop custom functions created for the new schema
DROP FUNCTION IF EXISTS update_board_updated_at_column() CASCADE;
DROP FUNCTION IF EXISTS update_board_state_on_element_change() CASCADE;
DROP FUNCTION IF EXISTS get_board_statistics(UUID) CASCADE;
DROP FUNCTION IF EXISTS auto_layout_elements(UUID, TEXT) CASCADE;
DROP FUNCTION IF EXISTS validate_board_state(UUID) CASCADE;

-- Commit transaction
COMMIT;

-- Verify rollback
DO $$
DECLARE
    board_count INTEGER;
    element_count INTEGER;
    connection_count INTEGER;
    note_count INTEGER;
BEGIN
    -- Get counts from original boards table
    SELECT COUNT(*) INTO board_count FROM boards;
    
    -- Count elements in JSONB
    SELECT SUM(jsonb_array_length(COALESCE(elements, '[]'::JSONB))) INTO element_count FROM boards;
    
    -- Count connections in JSONB
    SELECT SUM(jsonb_array_length(COALESCE(connections, '[]'::JSONB))) INTO connection_count FROM boards;
    
    -- Count notes in JSONB
    SELECT SUM(
        CASE 
            WHEN notes IS NULL OR notes = '{}'::JSONB THEN 0
            ELSE jsonb_object_keys(notes) | COUNT(*)
        END
    ) INTO note_count FROM boards;

    -- Log results
    RAISE NOTICE 'Board state rollback completed successfully:';
    RAISE NOTICE 'Boards restored: %', board_count;
    RAISE NOTICE 'Elements restored: %', COALESCE(element_count, 0);
    RAISE NOTICE 'Connections restored: %', COALESCE(connection_count, 0);
    RAISE NOTICE 'Notes restored: %', COALESCE(note_count, 0);
    
    -- Check for any issues
    IF board_count = 0 THEN
        RAISE NOTICE 'No boards found to rollback. This might be expected if no boards existed.';
    END IF;
END $$; 