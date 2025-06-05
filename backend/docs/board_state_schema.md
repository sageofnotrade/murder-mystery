# Board State Schema Documentation

This document describes the enhanced database schema for storing detective board state in the Murþrą mystery game.

## Overview

The board state schema replaces the simple JSONB-based `boards` table with a comprehensive relational structure that provides:

- **Better Performance**: Indexed queries on board elements and connections
- **Data Integrity**: Foreign key constraints and validation rules
- **Scalability**: Optimized for complex board operations
- **Flexibility**: Support for advanced features like layouts, themes, and annotations
- **Auditability**: Full tracking of user actions and changes

## Schema Design Principles

1. **Normalization**: Separate entities into dedicated tables for better performance
2. **User Isolation**: Row Level Security (RLS) ensures users only access their own data
3. **Referential Integrity**: Foreign key constraints maintain data consistency
4. **Extensibility**: JSONB fields allow for future feature additions
5. **Performance**: Strategic indexing for common query patterns

## Entity Relationship Diagram (ERD)

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   auth.users    │    │    mysteries    │    │  board_states   │
│                 │    │                 │    │                 │
│ • id (PK)       │───▶│ • id (PK)       │───▶│ • id (PK)       │
│ • email         │    │ • user_id (FK)  │    │ • mystery_id    │
│ • ...           │    │ • title         │    │ • user_id (FK)  │
└─────────────────┘    │ • ...           │    │ • name          │
                       └─────────────────┘    │ • zoom_level    │
                                              │ • pan_x, pan_y  │
                                              │ • theme         │
                                              │ • ...           │
                                              └─────────────────┘
                                                       │
                         ┌─────────────────────────────┼─────────────────────────────┐
                         │                             │                             │
                         ▼                             ▼                             ▼
                ┌─────────────────┐           ┌─────────────────┐           ┌─────────────────┐
                │ board_elements  │           │board_connections│           │  board_notes    │
                │                 │           │                 │           │                 │
                │ • id (PK)       │◄─────────▶│ • id (PK)       │           │ • id (PK)       │
                │ • board_id (FK) │           │ • board_id (FK) │           │ • board_id (FK) │
                │ • element_type  │           │ • source_id (FK)│           │ • note_type     │
                │ • title         │           │ • target_id (FK)│           │ • content       │
                │ • position_x    │           │ • conn_type     │           │ • position_x    │
                │ • position_y    │           │ • label         │           │ • position_y    │
                │ • content       │           │ • strength      │           │ • color         │
                │ • ...           │           │ • ...           │           │ • ...           │
                └─────────────────┘           └─────────────────┘           └─────────────────┘
                         │                                                           │
                         └─────────────────────┐                         ┌─────────┘
                                               ▼                         ▼
                                  ┌─────────────────────────────────────────┐
                                  │        board_layouts                    │
                                  │                                         │
                                  │ • id (PK)                              │
                                  │ • board_id (FK)                        │
                                  │ • name                                 │
                                  │ • layout_type                          │
                                  │ • element_positions (JSONB)            │
                                  │ • is_default                           │
                                  │ • ...                                  │
                                  └─────────────────────────────────────────┘
```

## Tables

### board_states

The main table that stores the overall state and configuration of each detective board.

| Column | Type | Description | Constraints |
|--------|------|-------------|------------|
| id | UUID | Primary key | DEFAULT uuid_generate_v4() |
| mystery_id | UUID | Reference to mysteries table | FK, ON DELETE CASCADE |
| user_id | UUID | Reference to auth.users | FK, ON DELETE CASCADE |
| created_at | TIMESTAMP | Creation timestamp | DEFAULT NOW() |
| updated_at | TIMESTAMP | Last update timestamp | DEFAULT NOW() |
| name | TEXT | Board display name | DEFAULT 'Detective Board' |
| description | TEXT | Board description | NULL |
| is_active | BOOLEAN | Whether board is active | DEFAULT TRUE |
| version | INTEGER | Board version number | DEFAULT 1 |
| zoom_level | FLOAT | Current zoom level | CHECK (0.1 <= zoom_level <= 3.0) |
| pan_x | FLOAT | Horizontal pan offset | DEFAULT 0.0 |
| pan_y | FLOAT | Vertical pan offset | DEFAULT 0.0 |
| grid_enabled | BOOLEAN | Grid visibility | DEFAULT TRUE |
| snap_to_grid | BOOLEAN | Snap elements to grid | DEFAULT FALSE |
| grid_size | INTEGER | Grid size in pixels | DEFAULT 20 |
| background_color | TEXT | Board background color | DEFAULT '#f5f5f5' |
| theme | TEXT | Board theme | CHECK IN ('default', 'dark', 'light', 'noir') |
| auto_save_enabled | BOOLEAN | Auto-save feature | DEFAULT TRUE |
| last_auto_save | TIMESTAMP | Last auto-save time | NULL |
| canvas_width | INTEGER | Canvas width in pixels | DEFAULT 1200 |
| canvas_height | INTEGER | Canvas height in pixels | DEFAULT 800 |

**Constraints:**
- UNIQUE(mystery_id, user_id) - One active board per user per mystery

### board_elements

Stores individual elements on the detective board (suspects, clues, locations, notes, etc.).

| Column | Type | Description | Constraints |
|--------|------|-------------|------------|
| id | UUID | Primary key | DEFAULT uuid_generate_v4() |
| board_id | UUID | Reference to board_states | FK, ON DELETE CASCADE |
| created_at | TIMESTAMP | Creation timestamp | DEFAULT NOW() |
| updated_at | TIMESTAMP | Last update timestamp | DEFAULT NOW() |
| element_type | TEXT | Type of element | CHECK IN ('suspect', 'clue', 'location', 'note', 'evidence', 'timeline', 'relationship') |
| title | TEXT | Element title | NOT NULL |
| description | TEXT | Element description | NULL |
| content | JSONB | Element-specific content | DEFAULT '{}' |
| position_x | FLOAT | X coordinate | NOT NULL, DEFAULT 0 |
| position_y | FLOAT | Y coordinate | NOT NULL, DEFAULT 0 |
| width | FLOAT | Element width | DEFAULT 120 |
| height | FLOAT | Element height | DEFAULT 70 |
| rotation | FLOAT | Rotation angle in degrees | DEFAULT 0 |
| z_index | INTEGER | Layer order | DEFAULT 1 |
| is_locked | BOOLEAN | Prevent modifications | DEFAULT FALSE |
| is_visible | BOOLEAN | Element visibility | DEFAULT TRUE |
| color | TEXT | Background color | DEFAULT '#ffffff' |
| border_color | TEXT | Border color | DEFAULT '#dddddd' |
| border_width | INTEGER | Border width in pixels | DEFAULT 1 |
| font_size | INTEGER | Font size | DEFAULT 12 |
| font_family | TEXT | Font family | DEFAULT 'Arial' |
| opacity | FLOAT | Element opacity | CHECK (0.0 <= opacity <= 1.0) |
| style_properties | JSONB | Additional style properties | DEFAULT '{}' |
| metadata | JSONB | Element metadata | DEFAULT '{}' |
| created_by_user | UUID | User who created element | FK to auth.users |
| last_modified_by | UUID | User who last modified | FK to auth.users |

### board_connections

Stores connections between board elements (threads, logical connections, etc.).

| Column | Type | Description | Constraints |
|--------|------|-------------|------------|
| id | UUID | Primary key | DEFAULT uuid_generate_v4() |
| board_id | UUID | Reference to board_states | FK, ON DELETE CASCADE |
| source_element_id | UUID | Source element | FK to board_elements, ON DELETE CASCADE |
| target_element_id | UUID | Target element | FK to board_elements, ON DELETE CASCADE |
| created_at | TIMESTAMP | Creation timestamp | DEFAULT NOW() |
| updated_at | TIMESTAMP | Last update timestamp | DEFAULT NOW() |
| connection_type | TEXT | Type of connection | CHECK IN ('thread', 'logic', 'alibi', 'evidence', 'causal', 'temporal', 'spatial', 'relationship') |
| label | TEXT | Connection label | NULL |
| description | TEXT | Connection description | NULL |
| strength | FLOAT | Connection strength | CHECK (0.0 <= strength <= 1.0) |
| confidence | FLOAT | Confidence level | CHECK (0.0 <= confidence <= 1.0) |
| is_bidirectional | BOOLEAN | Bidirectional connection | DEFAULT FALSE |
| line_style | TEXT | Visual line style | CHECK IN ('solid', 'dashed', 'dotted', 'dashdot') |
| line_width | INTEGER | Line width in pixels | DEFAULT 2 |
| line_color | TEXT | Line color | DEFAULT '#333333' |
| arrow_style | TEXT | Arrow style | CHECK IN ('arrow', 'circle', 'square', 'diamond', 'none') |
| curve_type | TEXT | Curve type | CHECK IN ('straight', 'bezier', 'arc') |
| control_points | JSONB | Bezier control points | DEFAULT '[]' |
| is_hidden | BOOLEAN | Connection visibility | DEFAULT FALSE |
| weight | FLOAT | Connection weight | DEFAULT 1.0 |
| metadata | JSONB | Connection metadata | DEFAULT '{}' |
| created_by_user | UUID | User who created connection | FK to auth.users |

**Constraints:**
- CHECK (source_element_id != target_element_id) - Prevent self-connections

### board_notes

Stores standalone notes and annotations on the board.

| Column | Type | Description | Constraints |
|--------|------|-------------|------------|
| id | UUID | Primary key | DEFAULT uuid_generate_v4() |
| board_id | UUID | Reference to board_states | FK, ON DELETE CASCADE |
| created_at | TIMESTAMP | Creation timestamp | DEFAULT NOW() |
| updated_at | TIMESTAMP | Last update timestamp | DEFAULT NOW() |
| note_type | TEXT | Type of note | CHECK IN ('note', 'annotation', 'reminder', 'question', 'hypothesis') |
| title | TEXT | Note title | NULL |
| content | TEXT | Note content | NOT NULL |
| position_x | FLOAT | X coordinate | NOT NULL, DEFAULT 0 |
| position_y | FLOAT | Y coordinate | NOT NULL, DEFAULT 0 |
| width | FLOAT | Note width | DEFAULT 200 |
| height | FLOAT | Note height | DEFAULT 150 |
| color | TEXT | Note background color | DEFAULT '#ffff88' |
| text_color | TEXT | Text color | DEFAULT '#000000' |
| font_size | INTEGER | Font size | DEFAULT 12 |
| is_pinned | BOOLEAN | Pin note to board | DEFAULT FALSE |
| is_minimized | BOOLEAN | Minimize note | DEFAULT FALSE |
| attached_to_element | UUID | Attached element | FK to board_elements, ON DELETE SET NULL |
| priority | INTEGER | Note priority (0-5) | CHECK (0 <= priority <= 5) |
| tags | JSONB | Note tags | DEFAULT '[]' |
| created_by_user | UUID | User who created note | FK to auth.users |

### board_layouts

Stores different board layout configurations for easy switching.

| Column | Type | Description | Constraints |
|--------|------|-------------|------------|
| id | UUID | Primary key | DEFAULT uuid_generate_v4() |
| board_id | UUID | Reference to board_states | FK, ON DELETE CASCADE |
| created_at | TIMESTAMP | Creation timestamp | DEFAULT NOW() |
| updated_at | TIMESTAMP | Last update timestamp | DEFAULT NOW() |
| name | TEXT | Layout name | NOT NULL |
| description | TEXT | Layout description | NULL |
| layout_type | TEXT | Layout algorithm | CHECK IN ('manual', 'auto_hierarchical', 'auto_circular', 'auto_force', 'timeline') |
| is_default | BOOLEAN | Default layout | DEFAULT FALSE |
| element_positions | JSONB | Element positions map | NOT NULL, DEFAULT '{}' |
| zoom_level | FLOAT | Layout zoom level | DEFAULT 1.0 |
| pan_x | FLOAT | Layout pan X | DEFAULT 0.0 |
| pan_y | FLOAT | Layout pan Y | DEFAULT 0.0 |
| algorithm_settings | JSONB | Layout algorithm settings | DEFAULT '{}' |
| created_by_user | UUID | User who created layout | FK to auth.users |

### board_element_connections

Junction table for many-to-many relationships between elements and connections.

| Column | Type | Description | Constraints |
|--------|------|-------------|------------|
| id | UUID | Primary key | DEFAULT uuid_generate_v4() |
| element_id | UUID | Element reference | FK to board_elements, ON DELETE CASCADE |
| connected_element_id | UUID | Connected element | FK to board_elements, ON DELETE CASCADE |
| connection_id | UUID | Connection reference | FK to board_connections, ON DELETE CASCADE |
| created_at | TIMESTAMP | Creation timestamp | DEFAULT NOW() |
| relationship_strength | FLOAT | Relationship strength | CHECK (0.0 <= relationship_strength <= 1.0) |

**Constraints:**
- CHECK (element_id != connected_element_id) - Prevent self-relationships
- UNIQUE(element_id, connected_element_id, connection_id) - Prevent duplicates

## Indexes

Strategic indexes are created for optimal query performance:

```sql
-- Board state indexes
CREATE INDEX idx_board_states_mystery_user ON board_states(mystery_id, user_id);
CREATE INDEX idx_board_states_active ON board_states(is_active);

-- Element indexes
CREATE INDEX idx_board_elements_board_id ON board_elements(board_id);
CREATE INDEX idx_board_elements_type ON board_elements(element_type);
CREATE INDEX idx_board_elements_position ON board_elements(position_x, position_y);
CREATE INDEX idx_board_elements_visible ON board_elements(is_visible);

-- Connection indexes
CREATE INDEX idx_board_connections_board_id ON board_connections(board_id);
CREATE INDEX idx_board_connections_source ON board_connections(source_element_id);
CREATE INDEX idx_board_connections_target ON board_connections(target_element_id);
CREATE INDEX idx_board_connections_type ON board_connections(connection_type);

-- Note indexes
CREATE INDEX idx_board_notes_board_id ON board_notes(board_id);
CREATE INDEX idx_board_notes_attached ON board_notes(attached_to_element);

-- Layout indexes
CREATE INDEX idx_board_layouts_board_id ON board_layouts(board_id);
CREATE INDEX idx_board_layouts_default ON board_layouts(is_default);
```

## Row Level Security (RLS)

All tables implement comprehensive RLS policies to ensure users can only access their own data:

```sql
-- Example RLS policy for board_elements
CREATE POLICY "Users can view elements of their boards"
    ON board_elements FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM board_states
            WHERE board_states.id = board_elements.board_id
            AND board_states.user_id = auth.uid()
        )
    );
```

## Utility Functions

The schema includes several utility functions for common operations:

### get_board_statistics(board_uuid UUID)

Returns comprehensive statistics about a board:

```sql
SELECT get_board_statistics('board-uuid-here');
-- Returns:
{
  "total_elements": 15,
  "elements_by_type": {
    "suspect": 4,
    "clue": 8,
    "location": 3
  },
  "total_connections": 12,
  "connections_by_type": {
    "thread": 8,
    "logic": 4
  },
  "total_notes": 5,
  "board_complexity": 3.2
}
```

### auto_layout_elements(board_uuid UUID, layout_algorithm TEXT)

Automatically arranges elements using specified algorithm:

```sql
SELECT auto_layout_elements('board-uuid-here', 'grid');
-- Returns element positions for grid layout
```

### validate_board_state(board_uuid UUID)

Validates board integrity and reports issues:

```sql
SELECT validate_board_state('board-uuid-here');
-- Returns:
{
  "is_valid": true,
  "issues": {
    "orphaned_connections": 0,
    "overlapping_elements": 2,
    "invalid_positions": 0
  },
  "warnings": ["Some elements are overlapping"]
}
```

## Migration Strategy

The schema includes comprehensive migration scripts:

1. **Forward Migration** (`003_board_state_migration.sql`)
   - Safely migrates from old JSONB structure
   - Preserves all existing data
   - Creates default layouts
   - Validates migration success

2. **Rollback Migration** (`003_board_state_rollback.sql`)
   - Reverts to original structure if needed
   - Maintains data integrity
   - Provides verification steps

## Performance Considerations

1. **Indexing Strategy**: Optimized for common query patterns
2. **Query Optimization**: Use specific indexes for filtering
3. **Connection Queries**: Leverage source/target indexes
4. **JSONB Usage**: Limited to flexible content that doesn't need frequent querying
5. **Batch Operations**: Use transactions for multiple related changes

## Usage Examples

### Create a New Board

```sql
INSERT INTO board_states (mystery_id, user_id, name, theme)
VALUES ('mystery-uuid', 'user-uuid', 'Investigation Board', 'noir');
```

### Add Elements to Board

```sql
INSERT INTO board_elements (board_id, element_type, title, position_x, position_y)
VALUES 
    ('board-uuid', 'suspect', 'John Doe', 100, 100),
    ('board-uuid', 'clue', 'Bloody Knife', 300, 150),
    ('board-uuid', 'location', 'Crime Scene', 200, 250);
```

### Create Connections

```sql
INSERT INTO board_connections (board_id, source_element_id, target_element_id, connection_type, label)
VALUES ('board-uuid', 'suspect-uuid', 'clue-uuid', 'evidence', 'Found at scene');
```

### Query Board with All Elements

```sql
SELECT 
    bs.*,
    json_agg(DISTINCT be.*) AS elements,
    json_agg(DISTINCT bc.*) AS connections,
    json_agg(DISTINCT bn.*) AS notes
FROM board_states bs
LEFT JOIN board_elements be ON be.board_id = bs.id AND be.is_visible = true
LEFT JOIN board_connections bc ON bc.board_id = bs.id AND bc.is_hidden = false
LEFT JOIN board_notes bn ON bn.board_id = bs.id
WHERE bs.mystery_id = 'mystery-uuid' AND bs.user_id = 'user-uuid'
GROUP BY bs.id;
```

## Schema Versioning

The schema includes version tracking in the `board_states` table to support future migrations and compatibility checks.

## Security Features

1. **Row Level Security**: Complete isolation between users
2. **Foreign Key Constraints**: Prevent orphaned records
3. **Check Constraints**: Validate data ranges and types
4. **Audit Trails**: Track who created/modified each element
5. **Soft Deletes**: Support for is_visible flags instead of hard deletes

## Future Enhancements

The schema is designed to support future features:

1. **Collaborative Boards**: Multi-user board sharing
2. **Board Templates**: Reusable board configurations
3. **Advanced Layouts**: AI-powered auto-arrangement
4. **Version History**: Board state snapshots
5. **Real-time Collaboration**: Live board updates
6. **Board Analytics**: Usage patterns and insights 