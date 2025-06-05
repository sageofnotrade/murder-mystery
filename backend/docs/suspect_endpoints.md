# Suspect Interaction Endpoints Documentation

## Overview

This document describes the suspect interaction endpoints implemented as part of BE-007. These endpoints provide comprehensive functionality for managing suspect profiles, generating dialogue, verifying alibis, and exploring motives within the murder mystery application.

## Architecture

The suspect interaction system consists of three main components:

1. **SuspectAgent** (`agents/suspect_agent.py`) - AI-powered agent for generating profiles and dialogue
2. **SuspectService** (`services/suspect_service.py`) - Business logic layer integrating with database
3. **SuspectRoutes** (`routes/suspect_routes.py`) - Flask API endpoints

## Authentication

All endpoints require JWT authentication via the `@jwt_required()` decorator. Include the JWT token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## API Endpoints

### 1. Get All Suspects

**GET** `/api/suspects`

Retrieve all suspects for a specific story.

**Query Parameters:**
- `story_id` (required): The story ID to get suspects for

**Response:**
```json
[
  {
    "id": "suspect-123",
    "story_id": "story-456",
    "name": "John Doe",
    "profile_data": { /* suspect profile */ },
    "state_data": { /* investigation state */ },
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

**Error Responses:**
- `400`: Missing story_id parameter
- `500`: Service error

### 2. Get Specific Suspect

**GET** `/api/suspects/{suspect_id}`

Retrieve details for a specific suspect.

**Parameters:**
- `suspect_id` (path): The suspect ID
- `story_id` (query, required): The story ID

**Response:**
```json
{
  "id": "suspect-123",
  "name": "John Doe",
  "profile_data": {
    "background": "Former accountant",
    "occupation": "Accountant",
    "motive": "Financial desperation",
    "alibi": "Claims to be at casino",
    "personality_traits": ["nervous", "evasive"],
    "relationship_to_victim": "Business partner",
    "suspicious_behaviors": ["avoiding eye contact"],
    "secrets": ["Hidden gambling addiction"]
  },
  "state_data": {
    "interviewed": true,
    "suspicious_level": 7,
    "known_information": ["Has gambling debts"],
    "contradictions": ["Time inconsistency"],
    "emotional_state": "nervous"
  }
}
```

**Error Responses:**
- `400`: Missing story_id parameter
- `404`: Suspect not found
- `500`: Service error

### 3. Create New Suspect

**POST** `/api/suspects`

Create a new suspect for a story.

**Request Body:**
```json
{
  "story_id": "story-456",
  "name": "Jane Smith",
  "profile_data": {
    "occupation": "Teacher",
    "background": "Local high school teacher"
  }
}
```

**Response:**
```json
{
  "id": "suspect-789",
  "story_id": "story-456",
  "name": "Jane Smith",
  "profile_data": { /* profile data */ },
  "state_data": { /* initial state */ },
  "created_at": "2024-01-01T00:00:00Z"
}
```

**Error Responses:**
- `400`: Invalid request data
- `500`: Service error

### 4. Generate Dialogue

**POST** `/api/suspects/{suspect_id}/dialogue`

Generate AI-powered dialogue with a suspect.

**Request Body:**
```json
{
  "question": "Where were you on the night of the murder?",
  "story_id": "story-456",
  "context": {
    "interrogation_style": "aggressive",
    "evidence_presented": ["fingerprints", "witness_statement"]
  }
}
```

**Response:**
```json
{
  "suspect_id": "suspect-123",
  "question": "Where were you on the night of the murder?",
  "dialogue": "I... I was at the casino all night! You can check with the dealers!",
  "updated_state": {
    "interviewed": true,
    "suspicious_level": 8,
    "emotional_state": "defensive",
    "contradictions": ["Time inconsistency", "Nervous behavior"]
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

**Error Responses:**
- `400`: Missing question or story_id
- `404`: Suspect not found
- `500`: Service error

### 5. Verify Alibi

**POST** `/api/suspects/{suspect_id}/verify-alibi`

Verify a suspect's alibi using AI analysis.

**Request Body:**
```json
{
  "story_id": "story-456",
  "alibi_details": {
    "location": "Golden Palace Casino",
    "time_start": "8:00 PM",
    "time_end": "2:00 AM",
    "witnesses": ["Dealer Mike", "Security camera"]
  },
  "evidence": [
    {
      "type": "video",
      "description": "Security footage",
      "supports_alibi": false,
      "details": "Shows suspect leaving at 11:30 PM"
    }
  ]
}
```

**Response:**
```json
{
  "suspect_id": "suspect-123",
  "alibi_verified": false,
  "verification_score": 45,
  "inconsistencies": [
    "Time discrepancy in security footage",
    "Suspect appears nervous during questioning"
  ],
  "dialogue_response": "I... well... maybe I left a bit earlier than I said...",
  "updated_state": {
    "suspicious_level": 9,
    "contradictions": ["Alibi timeline inconsistent"],
    "emotional_state": "nervous"
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

**Error Responses:**
- `400`: Missing story_id
- `404`: Suspect not found
- `500`: Service error

### 6. Get Suspect State

**GET** `/api/suspects/{suspect_id}/state`

Get the current investigation state of a suspect.

**Query Parameters:**
- `story_id` (required): The story ID

**Response:**
```json
{
  "name": "John Doe",
  "interviewed": true,
  "suspicious_level": 7,
  "known_information": ["Has gambling debts", "Access to victim's office"],
  "contradictions": ["Alibi timeline inconsistent"],
  "emotional_state": "nervous"
}
```

### 7. Update Suspect State

**PUT** `/api/suspects/{suspect_id}/state`

Update the investigation state of a suspect.

**Request Body:**
```json
{
  "story_id": "story-456",
  "state_updates": {
    "suspicious_level": 9,
    "emotional_state": "defensive",
    "known_information": ["Has gambling debts", "Lied about alibi"]
  }
}
```

**Response:**
```json
{
  "name": "John Doe",
  "interviewed": true,
  "suspicious_level": 9,
  "emotional_state": "defensive",
  "known_information": ["Has gambling debts", "Lied about alibi"],
  "contradictions": ["Alibi timeline inconsistent"]
}
```

### 8. Explore Motives

**GET** `/api/suspects/{suspect_id}/motives`

Use AI to explore potential motives for a suspect.

**Query Parameters:**
- `story_id` (required): The story ID

**Response:**
```json
{
  "suspect_id": "suspect-123",
  "current_motive": "Financial desperation",
  "potential_motives": "Financial gain, revenge against business partner, fear of exposure",
  "psychological_profile": ["impulsive", "desperate", "cunning"],
  "relationship_factors": "Business partner with access to finances",
  "behavioral_indicators": ["nervous", "evasive", "defensive"],
  "analysis_sources": ["psychological analysis", "behavioral patterns"],
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 9. Generate Suspect Profile

**POST** `/api/suspects/{suspect_id}/generate`

Generate or regenerate a suspect profile using AI.

**Request Body:**
```json
{
  "story_id": "story-456",
  "prompt": "Create a detailed profile for a suspect who is a former accountant with gambling problems",
  "context": {
    "crime_type": "embezzlement_murder",
    "setting": "corporate_office",
    "victim_relationship": "business_partner"
  }
}
```

**Response:**
```json
{
  "suspect_id": "suspect-123",
  "generated_profile": {
    "name": "John Doe",
    "background": "Former CPA with 15 years experience, developed gambling addiction after divorce",
    "occupation": "Accountant",
    "motive": "Desperate to cover embezzled funds before audit",
    "alibi": "Claims to have been at casino during time of murder",
    "personality_traits": ["intelligent", "desperate", "deceptive"],
    "relationship_to_victim": "Business partner and co-owner of accounting firm",
    "suspicious_behaviors": ["nervousness", "inconsistent statements"],
    "secrets": ["Embezzled $50,000", "Gambling addiction", "Pending divorce"]
  },
  "sources": ["criminal psychology database", "case study analysis"],
  "generation_prompt": "Create a detailed profile...",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## Data Models

### SuspectProfile
```python
{
  "name": str,
  "background": str,
  "occupation": Optional[str],
  "motive": Optional[str],
  "alibi": Optional[str],
  "personality_traits": List[str],
  "relationship_to_victim": Optional[str],
  "suspicious_behaviors": List[str],
  "secrets": List[str]
}
```

### SuspectState
```python
{
  "name": str,
  "interviewed": bool,
  "suspicious_level": int,  # 0-10 scale
  "known_information": List[str],
  "contradictions": List[str],
  "emotional_state": Optional[str]  # "calm", "nervous", "defensive", etc.
}
```

## Integration with SuspectAgent

The endpoints integrate with the SuspectAgent which provides:

1. **AI-powered dialogue generation** using LLM models
2. **Behavioral analysis** based on psychological patterns
3. **Alibi verification** using reasoning and evidence analysis
4. **Memory integration** with Mem0 for conversation context
5. **Web search integration** for realistic profile generation

## Error Handling

All endpoints include comprehensive error handling:

- **400 Bad Request**: Invalid request data or missing required fields
- **401 Unauthorized**: Missing or invalid JWT token
- **404 Not Found**: Suspect or resource not found
- **500 Internal Server Error**: Service errors or unexpected exceptions

Error responses include detailed error messages and validation details where applicable.

## Testing

The implementation includes comprehensive unit tests in `tests/test_suspect_routes.py` covering:

- All endpoint scenarios (success and error cases)
- Authentication requirements
- Input validation
- Service integration
- Error handling

Run tests with:
```bash
python -m pytest tests/test_suspect_routes.py -v
```

## Security Considerations

1. **Authentication**: All endpoints require valid JWT tokens
2. **Authorization**: Users can only access suspects from their own stories
3. **Input Validation**: All input is validated using Pydantic models
4. **SQL Injection Protection**: Uses parameterized queries via Supabase
5. **Rate Limiting**: Consider implementing rate limiting for AI-powered endpoints

## Performance Considerations

1. **Caching**: Consider caching suspect profiles and states
2. **Async Operations**: Service methods are async-compatible
3. **Database Optimization**: Efficient queries with proper indexing
4. **AI Model Selection**: Uses ModelRouter for optimal model selection based on task

## Dependencies

- Flask and Flask-JWT-Extended for API framework
- Pydantic for data validation
- SuspectAgent for AI capabilities
- Supabase for database operations
- Mem0 for memory management (optional)

## Future Enhancements

1. **Real-time updates**: WebSocket support for live suspect state changes
2. **Advanced analytics**: Suspect behavior tracking and patterns
3. **Multi-language support**: Dialogue generation in multiple languages
4. **Voice integration**: Speech-to-text for dialogue input
5. **Visual profiles**: AI-generated suspect images 