# Story State Schema Documentation

This document describes the database schema for storing story state in the Murþrą mystery game.

## Overview

The story state schema consists of several interconnected tables that track the progress and state of each player's mystery story. The schema is designed to support:

- Story progression tracking
- Player actions and choices
- Clue discovery and management
- Suspect interactions and relationships
- Game difficulty and progress
- Player achievements and statistics

## Tables

### story_states

The main table that tracks the overall state of a story.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| story_id | UUID | Reference to stories table |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |
| current_scene | TEXT | Current scene identifier |
| narrative_history | JSONB | Array of narrative segments |
| player_state | JSONB | Player-specific state data |
| game_progress | FLOAT | Overall story progress (0-1) |
| is_completed | BOOLEAN | Story completion status |
| completion_time | TIMESTAMP | When the story was completed |
| difficulty_level | TEXT | Story difficulty ('easy', 'medium', 'hard') |
| player_profile | JSONB | Player profile data |
| achievement_progress | JSONB | Achievement tracking |
| game_settings | JSONB | Game configuration |
| last_save_point | JSONB | Last saved state |

### story_actions

Tracks all player actions in the story.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| story_id | UUID | Reference to stories table |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |
| action_type | TEXT | Type of action |
| content | JSONB | Action details |
| result | JSONB | Action outcome |
| success | BOOLEAN | Action success status |
| difficulty_rating | FLOAT | Base difficulty |
| time_taken | INTEGER | Time taken in seconds |
| scene_location | TEXT | Where action occurred |
| player_skill_level | FLOAT | Player's skill level |
| difficulty_multiplier | FLOAT | Difficulty adjustment |
| success_probability | FLOAT | Success chance |
| actual_difficulty | FLOAT | Computed difficulty |

### story_choices

Records player choices and their consequences.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| story_id | UUID | Reference to stories table |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |
| choice_text | TEXT | Choice description |
| consequences | JSONB | Choice outcomes |
| is_selected | BOOLEAN | Whether choice was made |
| selection_time | TIMESTAMP | When choice was made |
| impact_score | FLOAT | Choice impact (-1 to 1) |
| difficulty_level | TEXT | Choice difficulty |
| required_skills | JSONB | Required player skills |
| skill_impact | JSONB | Skill effects |

### story_clues

Manages discovered clues and their properties.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| story_id | UUID | Reference to stories table |
| template_clue_id | UUID | Reference to template clues |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |
| discovered_at | TIMESTAMP | When clue was found |
| discovery_method | TEXT | How clue was found |
| discovery_location | TEXT | Where clue was found |
| relevance_score | FLOAT | Clue importance (0-1) |
| is_red_herring | BOOLEAN | Whether clue is misleading |
| notes | TEXT | Player notes |
| connections | JSONB | Related clues |

### story_suspects

Tracks suspect states and interactions.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| story_id | UUID | Reference to stories table |
| template_suspect_id | UUID | Reference to template suspects |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |
| trust_level | FLOAT | Trust rating (-1 to 1) |
| suspicion_level | FLOAT | Suspicion level (0-1) |
| alibi_status | TEXT | Alibi verification status |
| interrogation_history | JSONB | Past interrogations |
| personality_insights | JSONB | Discovered traits |
| relationship_level | FLOAT | Relationship status |
| known_secrets | JSONB | Discovered secrets |
| interaction_history | JSONB | Past interactions |

## Functions

### calculate_story_progress

Calculates the overall progress of a story based on:
- Completed actions (40% weight)
- Discovered clues (40% weight)
- Suspect interrogations (20% weight)

### get_story_statistics

Returns statistics for a story including:
- Total actions
- Successful actions
- Average difficulty
- Total play time

## Triggers

### update_story_progress

Automatically updates the story progress when:
- New actions are performed
- Clues are discovered
- Suspects are interrogated

## Indexes

The schema includes indexes for:
- Story IDs
- Action types
- Clue discovery times
- Choice selection status
- Suspect alibi status
- Difficulty levels
- Relationship levels

## Security

All tables have Row Level Security (RLS) policies that ensure:
- Users can only access their own stories
- Story data is properly isolated
- Actions are properly authorized

## Usage Examples

### Get Story Progress

```sql
SELECT game_progress 
FROM story_states 
WHERE story_id = '123e4567-e89b-12d3-a456-426614174000';
```

### Get Story Statistics

```sql
SELECT get_story_statistics('123e4567-e89b-12d3-a456-426614174000');
```

### Get Recent Actions

```sql
SELECT * 
FROM story_actions 
WHERE story_id = '123e4567-e89b-12d3-a456-426614174000' 
ORDER BY created_at DESC 
LIMIT 10;
```

### Get Discovered Clues

```sql
SELECT * 
FROM story_clues 
WHERE story_id = '123e4567-e89b-12d3-a456-426614174000' 
AND is_red_herring = false;
```

## Maintenance

The schema includes:
- Automatic timestamp updates
- Progress calculation triggers
- Data integrity constraints
- Performance optimizations

## Future Enhancements

Potential future improvements:
1. Add support for multiple save points
2. Implement branching narrative tracking
3. Add support for multiplayer interactions
4. Enhance achievement system
5. Add support for story replay 