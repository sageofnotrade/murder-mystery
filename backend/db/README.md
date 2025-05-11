# Murþrą Database Schema

This directory contains the database schema and initialization scripts for the Murþrą application.

## Schema Overview

### Tables

1. **profiles**
   - Stores user profiles and psychological traits
   - Links to Supabase auth.users
   - Fields:
     - `id`: UUID (Primary Key)
     - `user_id`: UUID (Foreign Key to auth.users)
     - `psychological_traits`: JSONB (User's psychological profile)
     - `preferences`: JSONB (User preferences)
     - `play_history`: JSONB (Game history)

2. **mystery_templates**
   - Stores templates for different types of mysteries
   - Fields:
     - `id`: UUID (Primary Key)
     - `title`: TEXT
     - `description`: TEXT
     - `difficulty`: TEXT (easy/medium/hard)
     - `structure`: JSONB (Template structure)
     - `is_public`: BOOLEAN

3. **mysteries**
   - Stores user's active mysteries
   - Fields:
     - `id`: UUID (Primary Key)
     - `user_id`: UUID (Foreign Key to auth.users)
     - `template_id`: UUID (Foreign Key to mystery_templates)
     - `title`: TEXT
     - `state`: JSONB (Current game state)
     - `is_completed`: BOOLEAN

4. **stories**
   - Stores narrative progression
   - Fields:
     - `id`: UUID (Primary Key)
     - `mystery_id`: UUID (Foreign Key to mysteries)
     - `current_scene`: TEXT
     - `narrative_history`: JSONB
     - `discovered_clues`: JSONB
     - `suspect_states`: JSONB

5. **boards**
   - Stores visual board state
   - Fields:
     - `id`: UUID (Primary Key)
     - `mystery_id`: UUID (Foreign Key to mysteries)
     - `elements`: JSONB (Board elements)
     - `connections`: JSONB (Element connections)
     - `notes`: JSONB (User notes)
     - `layout`: JSONB (Board layout)

## Security

All tables have Row Level Security (RLS) policies that ensure:
- Users can only access their own data
- Users can only modify their own data
- Proper cascading deletes when users are removed

## Automatic Updates

All tables have:
- `created_at`: Automatically set on creation
- `updated_at`: Automatically updated on modification

## Usage

1. Initialize the database:
   ```bash
   python db/init_db.py
   ```

2. View the schema:
   ```bash
   cat db/schema.sql
   ```

## Notes

- All timestamps are in UTC
- JSONB is used for flexible schema fields
- UUIDs are used for all IDs
- Foreign keys have ON DELETE CASCADE where appropriate 