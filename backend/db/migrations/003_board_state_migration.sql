-- Migration script for board state schema
-- This script safely migrates data from the old boards table to the new schema

-- Start transaction
BEGIN;

-- Create temporary table to store existing board data
CREATE TEMPORARY TABLE temp_boards AS
SELECT 
    id,
    mystery_id,
    created_at,
    updated_at,
    elements,
    connections,
    notes,
    layout
FROM boards
WHERE EXISTS (SELECT 1 FROM boards LIMIT 1);

-- Run the new schema creation
\i ../board_state_schema.sql

-- Migrate data to board_states
INSERT INTO board_states (
    id,
    mystery_id,
    user_id,
    created_at,
    updated_at,
    name,
    description,
    is_active,
    version,
    zoom_level,
    pan_x,
    pan_y,
    grid_enabled,
    snap_to_grid,
    grid_size,
    background_color,
    theme,
    auto_save_enabled,
    canvas_width,
    canvas_height
)
SELECT 
    tb.id,
    tb.mystery_id,
    m.user_id, -- Get user_id from mysteries table
    tb.created_at,
    tb.updated_at,
    'Detective Board', -- Default name
    'Migrated from legacy board', -- Default description
    TRUE, -- Default active
    1, -- Default version
    COALESCE((tb.layout->>'zoom')::FLOAT, 1.0), -- Extract zoom from layout or default
    COALESCE((tb.layout->>'pan_x')::FLOAT, 0.0), -- Extract pan_x from layout or default
    COALESCE((tb.layout->>'pan_y')::FLOAT, 0.0), -- Extract pan_y from layout or default
    TRUE, -- Default grid enabled
    FALSE, -- Default snap to grid
    20, -- Default grid size
    '#f5f5f5', -- Default background color
    'default', -- Default theme
    TRUE, -- Default auto save enabled
    1200, -- Default canvas width
    800 -- Default canvas height
FROM temp_boards tb
JOIN mysteries m ON m.id = tb.mystery_id;

-- Migrate elements from JSONB to board_elements table
INSERT INTO board_elements (
    id,
    board_id,
    created_at,
    updated_at,
    element_type,
    title,
    description,
    content,
    position_x,
    position_y,
    width,
    height,
    rotation,
    z_index,
    is_locked,
    is_visible,
    color,
    border_color,
    border_width,
    font_size,
    font_family,
    opacity,
    style_properties,
    metadata,
    created_by_user
)
SELECT 
    COALESCE((element->>'id')::UUID, uuid_generate_v4()),
    tb.id, -- board_id
    tb.created_at,
    tb.updated_at,
    COALESCE(element->>'type', 'note'), -- element_type with fallback
    COALESCE(element->>'title', element->>'name', 'Untitled'), -- title with fallbacks
    element->>'description',
    COALESCE(element->'properties', element->'content', '{}'::JSONB), -- content
    COALESCE((element->'position'->>'x')::FLOAT, 100), -- position_x with fallback
    COALESCE((element->'position'->>'y')::FLOAT, 100), -- position_y with fallback
    COALESCE((element->>'width')::FLOAT, 120), -- width with fallback
    COALESCE((element->>'height')::FLOAT, 70), -- height with fallback
    COALESCE((element->>'rotation')::FLOAT, 0), -- rotation with fallback
    COALESCE((element->>'z_index')::INTEGER, 1), -- z_index with fallback
    COALESCE((element->>'locked')::BOOLEAN, FALSE), -- is_locked with fallback
    COALESCE((element->>'visible')::BOOLEAN, TRUE), -- is_visible with fallback
    COALESCE(element->>'color', '#ffffff'), -- color with fallback
    COALESCE(element->>'border_color', '#dddddd'), -- border_color with fallback
    COALESCE((element->>'border_width')::INTEGER, 1), -- border_width with fallback
    COALESCE((element->>'font_size')::INTEGER, 12), -- font_size with fallback
    COALESCE(element->>'font_family', 'Arial'), -- font_family with fallback
    COALESCE((element->>'opacity')::FLOAT, 1.0), -- opacity with fallback
    COALESCE(element->'style', '{}'::JSONB), -- style_properties
    COALESCE(element->'metadata', '{}'::JSONB), -- metadata
    m.user_id -- created_by_user
FROM temp_boards tb
JOIN mysteries m ON m.id = tb.mystery_id,
jsonb_array_elements(COALESCE(tb.elements, '[]'::JSONB)) AS element;

-- Migrate connections from JSONB to board_connections table
INSERT INTO board_connections (
    id,
    board_id,
    source_element_id,
    target_element_id,
    created_at,
    updated_at,
    connection_type,
    label,
    description,
    strength,
    confidence,
    is_bidirectional,
    line_style,
    line_width,
    line_color,
    arrow_style,
    curve_type,
    control_points,
    is_hidden,
    weight,
    metadata,
    created_by_user
)
SELECT 
    COALESCE((connection->>'id')::UUID, uuid_generate_v4()),
    tb.id, -- board_id
    tb.created_at,
    tb.updated_at,
    -- Find source element UUID by matching legacy ID
    (SELECT be.id FROM board_elements be 
     WHERE be.board_id = tb.id 
     AND (be.metadata->>'legacy_id' = connection->>'sourceId' 
          OR be.metadata->>'legacy_id' = connection->>'source_id'
          OR be.title = connection->>'sourceId')
     LIMIT 1),
    -- Find target element UUID by matching legacy ID  
    (SELECT be.id FROM board_elements be 
     WHERE be.board_id = tb.id 
     AND (be.metadata->>'legacy_id' = connection->>'targetId' 
          OR be.metadata->>'legacy_id' = connection->>'target_id'
          OR be.title = connection->>'targetId')
     LIMIT 1),
    COALESCE(connection->>'type', 'thread'), -- connection_type with fallback
    connection->>'label',
    connection->>'description',
    COALESCE((connection->>'strength')::FLOAT, 1.0), -- strength with fallback
    COALESCE((connection->>'confidence')::FLOAT, 1.0), -- confidence with fallback
    COALESCE((connection->>'bidirectional')::BOOLEAN, FALSE), -- is_bidirectional
    COALESCE(connection->>'line_style', 'solid'), -- line_style with fallback
    COALESCE((connection->>'line_width')::INTEGER, 2), -- line_width with fallback
    COALESCE(connection->>'line_color', '#333333'), -- line_color with fallback
    COALESCE(connection->>'arrow_style', 'arrow'), -- arrow_style with fallback
    COALESCE(connection->>'curve_type', 'bezier'), -- curve_type with fallback
    COALESCE(connection->'control_points', '[]'::JSONB), -- control_points
    COALESCE((connection->>'hidden')::BOOLEAN, FALSE), -- is_hidden
    COALESCE((connection->>'weight')::FLOAT, 1.0), -- weight with fallback
    COALESCE(connection->'metadata', '{}'::JSONB), -- metadata
    m.user_id -- created_by_user
FROM temp_boards tb
JOIN mysteries m ON m.id = tb.mystery_id,
jsonb_array_elements(COALESCE(tb.connections, '[]'::JSONB)) AS connection
WHERE connection->>'sourceId' IS NOT NULL 
  AND connection->>'targetId' IS NOT NULL;

-- Migrate notes from JSONB to board_notes table
INSERT INTO board_notes (
    id,
    board_id,
    created_at,
    updated_at,
    note_type,
    title,
    content,
    position_x,
    position_y,
    width,
    height,
    color,
    text_color,
    font_size,
    is_pinned,
    is_minimized,
    attached_to_element,
    priority,
    tags,
    created_by_user
)
SELECT 
    COALESCE((note_value->>'id')::UUID, uuid_generate_v4()),
    tb.id, -- board_id
    tb.created_at,
    tb.updated_at,
    COALESCE(note_value->>'type', 'note'), -- note_type with fallback
    note_value->>'title',
    COALESCE(note_value->>'content', note_value->>'text', 'Empty note'), -- content with fallbacks
    COALESCE((note_value->'position'->>'x')::FLOAT, 100), -- position_x with fallback
    COALESCE((note_value->'position'->>'y')::FLOAT, 100), -- position_y with fallback
    COALESCE((note_value->>'width')::FLOAT, 200), -- width with fallback
    COALESCE((note_value->>'height')::FLOAT, 150), -- height with fallback
    COALESCE(note_value->>'color', '#ffff88'), -- color with fallback
    COALESCE(note_value->>'text_color', '#000000'), -- text_color with fallback
    COALESCE((note_value->>'font_size')::INTEGER, 12), -- font_size with fallback
    COALESCE((note_value->>'pinned')::BOOLEAN, FALSE), -- is_pinned
    COALESCE((note_value->>'minimized')::BOOLEAN, FALSE), -- is_minimized
    NULL, -- attached_to_element (will be updated separately if needed)
    COALESCE((note_value->>'priority')::INTEGER, 0), -- priority with fallback
    COALESCE(note_value->'tags', '[]'::JSONB), -- tags
    m.user_id -- created_by_user
FROM temp_boards tb
JOIN mysteries m ON m.id = tb.mystery_id,
jsonb_each(COALESCE(tb.notes, '{}'::JSONB)) AS note_entry(note_key, note_value);

-- Create default layout for each migrated board
INSERT INTO board_layouts (
    board_id,
    created_at,
    updated_at,
    name,
    description,
    layout_type,
    is_default,
    element_positions,
    zoom_level,
    pan_x,
    pan_y,
    algorithm_settings,
    created_by_user
)
SELECT 
    bs.id, -- board_id
    bs.created_at,
    bs.updated_at,
    'Default Layout', -- name
    'Migrated default layout', -- description
    'manual', -- layout_type
    TRUE, -- is_default
    COALESCE(
        jsonb_object_agg(
            be.id::TEXT, 
            jsonb_build_object('x', be.position_x, 'y', be.position_y)
        ), 
        '{}'::JSONB
    ), -- element_positions
    bs.zoom_level,
    bs.pan_x,
    bs.pan_y,
    '{}'::JSONB, -- algorithm_settings
    bs.user_id -- created_by_user
FROM board_states bs
LEFT JOIN board_elements be ON be.board_id = bs.id
GROUP BY bs.id, bs.created_at, bs.updated_at, bs.zoom_level, bs.pan_x, bs.pan_y, bs.user_id;

-- Update element metadata to store legacy IDs for reference
UPDATE board_elements 
SET metadata = metadata || jsonb_build_object('migrated_from', 'legacy_boards')
WHERE board_id IN (SELECT id FROM temp_boards);

-- Clean up orphaned connections (where source or target elements couldn't be found)
DELETE FROM board_connections 
WHERE source_element_id IS NULL OR target_element_id IS NULL;

-- Drop the old boards table (commented out for safety - uncomment when ready)
-- DROP TABLE boards;

-- Drop temporary table
DROP TABLE temp_boards;

-- Create views for backward compatibility (optional)
CREATE OR REPLACE VIEW legacy_boards AS
SELECT 
    bs.id,
    bs.mystery_id,
    bs.created_at,
    bs.updated_at,
    COALESCE(
        jsonb_agg(
            jsonb_build_object(
                'id', be.id,
                'type', be.element_type,
                'title', be.title,
                'description', be.description,
                'position', jsonb_build_object('x', be.position_x, 'y', be.position_y),
                'properties', be.content
            )
        ) FILTER (WHERE be.id IS NOT NULL),
        '[]'::JSONB
    ) AS elements,
    COALESCE(
        (SELECT jsonb_agg(
            jsonb_build_object(
                'id', bc.id,
                'sourceId', bc.source_element_id,
                'targetId', bc.target_element_id,
                'type', bc.connection_type,
                'label', bc.label,
                'strength', bc.strength
            )
        )
        FROM board_connections bc 
        WHERE bc.board_id = bs.id),
        '[]'::JSONB
    ) AS connections,
    COALESCE(
        (SELECT jsonb_object_agg(
            bn.id::TEXT,
            jsonb_build_object(
                'title', bn.title,
                'content', bn.content,
                'position', jsonb_build_object('x', bn.position_x, 'y', bn.position_y)
            )
        )
        FROM board_notes bn 
        WHERE bn.board_id = bs.id),
        '{}'::JSONB
    ) AS notes,
    jsonb_build_object(
        'zoom', bs.zoom_level,
        'pan_x', bs.pan_x,
        'pan_y', bs.pan_y
    ) AS layout
FROM board_states bs
LEFT JOIN board_elements be ON be.board_id = bs.id AND be.is_visible = true
GROUP BY bs.id, bs.mystery_id, bs.created_at, bs.updated_at, bs.zoom_level, bs.pan_x, bs.pan_y;

-- Commit transaction
COMMIT;

-- Verify migration
DO $$
DECLARE
    board_count INTEGER;
    element_count INTEGER;
    connection_count INTEGER;
    note_count INTEGER;
    layout_count INTEGER;
BEGIN
    -- Get counts
    SELECT COUNT(*) INTO board_count FROM board_states;
    SELECT COUNT(*) INTO element_count FROM board_elements;
    SELECT COUNT(*) INTO connection_count FROM board_connections;
    SELECT COUNT(*) INTO note_count FROM board_notes;
    SELECT COUNT(*) INTO layout_count FROM board_layouts;

    -- Log results
    RAISE NOTICE 'Board state migration completed successfully:';
    RAISE NOTICE 'Boards migrated: %', board_count;
    RAISE NOTICE 'Elements created: %', element_count;
    RAISE NOTICE 'Connections created: %', connection_count;
    RAISE NOTICE 'Notes created: %', note_count;
    RAISE NOTICE 'Layouts created: %', layout_count;
    
    -- Check for any issues
    IF board_count = 0 THEN
        RAISE NOTICE 'No boards found to migrate. This might be expected if no boards existed.';
    END IF;
    
    -- Check for orphaned connections
    DECLARE
        orphaned_count INTEGER;
    BEGIN
        SELECT COUNT(*) INTO orphaned_count
        FROM board_connections bc
        WHERE NOT EXISTS (
            SELECT 1 FROM board_elements be1 
            WHERE be1.id = bc.source_element_id
        ) OR NOT EXISTS (
            SELECT 1 FROM board_elements be2 
            WHERE be2.id = bc.target_element_id
        );
        
        IF orphaned_count > 0 THEN
            RAISE WARNING 'Found % orphaned connections that were cleaned up', orphaned_count;
        END IF;
    END;
END $$; 