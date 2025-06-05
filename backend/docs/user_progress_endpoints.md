# User Progress Endpoints Documentation

## Overview

The User Progress API provides comprehensive endpoints for saving, loading, and managing user progress through mysteries. This includes save/load functionality, achievement tracking, statistics, and analytics.

## Base URL

All endpoints are prefixed with `/api/progress`

## Authentication

All endpoints require JWT authentication via the `Authorization: Bearer <token>` header.

## Endpoints

### 1. Get User Progress

**GET** `/api/progress`

Retrieve complete user progress including all mysteries and achievements.

**Query Parameters:**
- `include_details` (boolean, optional): Include mystery details. Default: `true`

**Response:**
```json
{
  "user_id": "user-123",
  "username": "detective_alice",
  "statistics": {
    "total_mysteries_started": 5,
    "total_mysteries_completed": 3,
    "total_play_time_minutes": 180,
    "total_clues_discovered": 25,
    "correct_deductions": 8,
    "incorrect_deductions": 2
  },
  "achievements": [
    {
      "id": "ach-1",
      "type": "first_mystery",
      "name": "First Case Closed",
      "description": "Complete your first mystery",
      "points": 100,
      "earned_at": "2024-01-15T10:30:00Z"
    }
  ],
  "achievement_points": 100,
  "mystery_progress": {
    "mystery-456": {
      "mystery_id": "mystery-456",
      "mystery_title": "The Case of the Missing Painting",
      "difficulty": "intermediate",
      "status": "in_progress",
      "progress_percentage": 65.0,
      "current_scene": "investigation"
    }
  },
  "current_mystery_id": "mystery-456"
}
```

### 2. Get Progress Summary

**GET** `/api/progress/summary`

Get a high-level summary of user progress.

**Response:**
```json
{
  "user_id": "user-123",
  "total_mysteries": 5,
  "completed_mysteries": 3,
  "current_mystery": "mystery-456",
  "achievement_count": 1,
  "total_play_time_hours": 3.0,
  "last_played": "2024-01-15T14:30:00Z",
  "progress_level": "Intermediate",
  "completion_rate": 60.0
}
```

### 3. Save Progress

**POST** `/api/progress/save`

Save user progress for a specific mystery.

**Request Body:**
```json
{
  "mystery_id": "mystery-456",
  "progress_data": {
    "current_scene": "investigation",
    "inventory": ["magnifying_glass", "key"],
    "discovered_evidence": ["fingerprint", "footprint"]
  },
  "checkpoint_name": "scene_1_complete",
  "auto_save": false
}
```

**Response:**
```json
{
  "success": true,
  "save_id": "save-789",
  "timestamp": "2024-01-15T14:30:00Z",
  "mystery_id": "mystery-456",
  "checkpoint_name": "scene_1_complete",
  "backup_created": false
}
```

### 4. Load Progress

**POST** `/api/progress/load`

Load user progress for a specific mystery or overall progress.

**Request Body:**
```json
{
  "mystery_id": "mystery-456",
  "checkpoint_name": "scene_1_complete",
  "include_statistics": true,
  "include_achievements": true
}
```

**Response:**
```json
{
  "user_progress": { /* UserProgress object */ },
  "mystery_progress": { /* MysteryProgress object */ },
  "last_save_timestamp": "2024-01-15T14:30:00Z",
  "available_checkpoints": ["auto_save", "scene_1_complete", "scene_2_start"]
}
```

### 5. Get Mystery Progress

**GET** `/api/progress/mystery/{mystery_id}`

Get progress for a specific mystery.

**Response:**
```json
{
  "mystery_id": "mystery-456",
  "mystery_title": "The Case of the Missing Painting",
  "difficulty": "intermediate",
  "status": "in_progress",
  "current_scene": "investigation",
  "progress_percentage": 65.0,
  "clues_discovered": [
    {"id": "clue-1", "name": "Fingerprint", "location": "Frame"}
  ],
  "suspects_questioned": ["John Doe", "Jane Smith"],
  "time_played_minutes": 45,
  "save_data": {
    "current_location": "gallery",
    "inventory": ["magnifying_glass"]
  }
}
```

### 6. Create Mystery Progress

**POST** `/api/progress/mystery/{mystery_id}`

Create new progress tracking for a mystery.

**Response:**
```json
{
  "mystery_id": "mystery-456",
  "mystery_title": "The Case of the Missing Painting",
  "difficulty": "intermediate",
  "status": "in_progress",
  "current_scene": "introduction",
  "progress_percentage": 0.0,
  "started_at": "2024-01-15T14:30:00Z"
}
```

### 7. Get Mystery Checkpoints

**GET** `/api/progress/mystery/{mystery_id}/checkpoints`

Get available checkpoints for a mystery.

**Response:**
```json
{
  "mystery_id": "mystery-456",
  "checkpoints": [
    {
      "name": "auto_save",
      "timestamp": "2024-01-15T14:30:00Z",
      "save_id": "save-789"
    },
    {
      "name": "scene_1_complete",
      "timestamp": "2024-01-15T13:45:00Z",
      "save_id": "save-788"
    }
  ],
  "total_count": 2
}
```

### 8. Load Checkpoint

**GET** `/api/progress/mystery/{mystery_id}/checkpoints/{checkpoint_name}`

Load a specific checkpoint for a mystery.

**Response:**
```json
{
  "user_progress": { /* UserProgress object */ },
  "mystery_progress": { /* MysteryProgress object with checkpoint data loaded */ },
  "last_save_timestamp": "2024-01-15T14:30:00Z",
  "available_checkpoints": ["auto_save", "scene_1_complete"]
}
```

### 9. Get Achievements

**GET** `/api/progress/achievements`

Get user's achievements.

**Response:**
```json
{
  "achievements": [
    {
      "id": "ach-1",
      "type": "first_mystery",
      "name": "First Case Closed",
      "description": "Complete your first mystery",
      "points": 100,
      "earned_at": "2024-01-15T10:30:00Z",
      "icon": "🏆"
    }
  ],
  "total_points": 100,
  "achievement_count": 1
}
```

### 10. Award Achievement

**POST** `/api/progress/achievements/{achievement_type}`

Award an achievement to the user.

**Request Body:**
```json
{
  "mystery_id": "mystery-456"
}
```

**Response:**
```json
{
  "achievement": {
    "id": "ach-2",
    "type": "quick_solver",
    "name": "Speed Detective",
    "description": "Solve a mystery in under 30 minutes",
    "points": 200,
    "earned_at": "2024-01-15T14:30:00Z",
    "icon": "⚡"
  },
  "newly_earned": true
}
```

### 11. Get Statistics

**GET** `/api/progress/statistics`

Get user's game statistics.

**Response:**
```json
{
  "total_mysteries_started": 5,
  "total_mysteries_completed": 3,
  "total_play_time_minutes": 180,
  "total_clues_discovered": 25,
  "total_suspects_questioned": 12,
  "correct_deductions": 8,
  "incorrect_deductions": 2,
  "hints_used": 5,
  "perfect_solves": 1,
  "current_solving_streak": 2,
  "best_solving_streak": 3,
  "last_played": "2024-01-15T14:30:00Z"
}
```

### 12. Get Current Mystery

**GET** `/api/progress/current-mystery`

Get the user's current mystery progress.

**Response:** Same as Get Mystery Progress

### 13. Set Current Mystery

**PUT** `/api/progress/current-mystery`

Set the user's current mystery.

**Request Body:**
```json
{
  "mystery_id": "mystery-456"
}
```

**Response:**
```json
{
  "current_mystery_id": "mystery-456",
  "mystery_progress": { /* MysteryProgress object */ }
}
```

### 14. Get Analytics

**GET** `/api/progress/analytics`

Get analytics data for user progress.

**Response:**
```json
{
  "user_id": "user-123",
  "session_count": 15,
  "average_session_duration": 45.5,
  "favorite_mystery_type": "detective",
  "peak_play_times": ["evening", "weekend"],
  "difficulty_preference": "intermediate",
  "completion_patterns": {
    "total_started": 5,
    "total_completed": 3,
    "completion_rate": 60.0
  },
  "improvement_metrics": {
    "average_hints_used": 1.2,
    "average_wrong_deductions": 0.8
  }
}
```

### 15. Create Backup

**POST** `/api/progress/backup`

Create a backup of user progress.

**Request Body:**
```json
{
  "backup_name": "weekly_backup",
  "include_save_states": true,
  "compress": true
}
```

**Response:**
```json
{
  "backup_id": "backup_user-123_20240115_143000",
  "created_at": "2024-01-15T14:30:00Z",
  "message": "Backup functionality coming soon"
}
```

### 16. Reset Progress

**POST** `/api/progress/reset`

Reset user progress (with confirmation).

**Request Body:**
```json
{
  "confirm": true
}
```

**Response:**
```json
{
  "message": "Progress reset functionality coming soon",
  "user_id": "user-123"
}
```

## Data Models

### Achievement Types

- `first_mystery` - Complete your first mystery
- `quick_solver` - Solve a mystery in under 30 minutes  
- `thorough_investigator` - Discover all clues in a mystery
- `clue_collector` - Discover 50 clues across all mysteries
- `master_interrogator` - Question all suspects in a mystery
- `perfect_deduction` - Solve a mystery without any wrong guesses
- `mystery_marathon` - Complete 10 mysteries
- `eagle_eye` - Find a hidden clue
- `persistence` - Play for 5 consecutive days
- `speed_demon` - Complete 3 mysteries in one day

### Progress Status

- `not_started` - Mystery not yet begun
- `in_progress` - Currently playing
- `completed` - Successfully completed
- `paused` - Temporarily stopped
- `abandoned` - Given up on mystery

### Difficulty Levels

- `beginner` - Easy mysteries for new players
- `intermediate` - Medium difficulty
- `advanced` - Challenging mysteries
- `expert` - Most difficult mysteries

## Error Handling

All endpoints return standardized error responses:

```json
{
  "error": "Error description",
  "details": { /* Additional error details */ },
  "timestamp": "2024-01-15T14:30:00Z"
}
```

Common HTTP status codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (missing/invalid JWT)
- `404` - Not Found
- `500` - Internal Server Error

## Integration Examples

### Frontend Save Game

```javascript
// Save progress when player completes a scene
const saveProgress = async (mysteryId, gameState) => {
  const response = await fetch('/api/progress/save', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${jwt_token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      mystery_id: mysteryId,
      progress_data: gameState,
      checkpoint_name: `scene_${gameState.current_scene}_complete`,
      auto_save: false
    })
  });
  
  return response.json();
};
```

### Frontend Load Game

```javascript
// Load progress when player starts a mystery
const loadProgress = async (mysteryId) => {
  const response = await fetch('/api/progress/load', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${jwt_token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      mystery_id: mysteryId,
      include_statistics: true
    })
  });
  
  return response.json();
};
```

### Auto-Save Implementation

```javascript
// Auto-save every 5 minutes
setInterval(async () => {
  if (gameState.mystery_id && gameState.hasUnsavedChanges) {
    await fetch('/api/progress/save', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${jwt_token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        mystery_id: gameState.mystery_id,
        progress_data: gameState,
        auto_save: true
      })
    });
    gameState.hasUnsavedChanges = false;
  }
}, 300000); // 5 minutes
```

## Database Schema

The user progress system requires the following database tables:

### user_progress
- `user_id` (VARCHAR, PRIMARY KEY)
- `username` (VARCHAR)
- `statistics` (JSONB)
- `achievements` (JSONB)
- `achievement_points` (INTEGER)
- `current_mystery_id` (VARCHAR)
- `preferences` (JSONB)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)
- `last_backup` (TIMESTAMP)

### mystery_progress
- `user_id` (VARCHAR)
- `mystery_id` (VARCHAR)
- `mystery_title` (VARCHAR)
- `difficulty` (VARCHAR)
- `status` (VARCHAR)
- `current_scene` (VARCHAR)
- `scenes_completed` (JSONB)
- `total_scenes` (INTEGER)
- `progress_percentage` (DECIMAL)
- `clues_discovered` (JSONB)
- `suspects_met` (JSONB)
- `suspects_questioned` (JSONB)
- `locations_visited` (JSONB)
- `choices_made` (JSONB)
- `actions_taken` (JSONB)
- `hints_used` (INTEGER)
- `wrong_deductions` (INTEGER)
- `investigation_score` (INTEGER)
- `started_at` (TIMESTAMP)
- `last_played` (TIMESTAMP)
- `completed_at` (TIMESTAMP)
- `time_played_minutes` (INTEGER)
- `save_data` (JSONB)
- `checkpoint_data` (JSONB)
- PRIMARY KEY (`user_id`, `mystery_id`)

## Security Considerations

1. **JWT Authentication** - All endpoints require valid JWT tokens
2. **User Isolation** - Users can only access their own progress data
3. **Input Validation** - All request data is validated using Pydantic models
4. **SQL Injection Prevention** - Using parameterized queries through Supabase client
5. **Rate Limiting** - Consider implementing rate limiting for save operations
6. **Data Encryption** - Sensitive save data should be encrypted in the database

## Performance Considerations

1. **Caching** - Progress data is cached for frequently accessed mysteries
2. **Pagination** - Large datasets should be paginated (achievements, analytics)
3. **Compression** - Save data can be compressed to reduce storage
4. **Async Operations** - All database operations are asynchronous
5. **Batch Updates** - Multiple progress updates can be batched for efficiency

## Future Enhancements

1. **Cloud Saves** - Sync progress across multiple devices
2. **Progress Sharing** - Share achievements and progress with friends
3. **Leaderboards** - Compare progress with other players
4. **Advanced Analytics** - Machine learning for personalized recommendations
5. **Real-time Updates** - WebSocket support for live progress updates
6. **Backup/Restore** - Full implementation of backup and restore functionality 