# Clue Management API Documentation

This document describes the endpoints available for managing clues in the Murþrą mystery game.

## Base URL

All endpoints are prefixed with `/api`

## Authentication

All endpoints require authentication. Include the authentication token in the request header:

```
Authorization: Bearer <token>
```

## Endpoints

### Get Story Clues

Retrieves all clues for a specific story.

```http
GET /stories/{story_id}/clues
```

#### Parameters

| Parameter | Type   | Description                    |
|-----------|--------|--------------------------------|
| story_id  | UUID   | The ID of the story to query   |

#### Response

```json
[
  {
    "id": "uuid",
    "story_id": "uuid",
    "template_clue_id": "uuid",
    "discovered_at": "ISO8601 datetime",
    "discovery_method": "string",
    "discovery_location": "string",
    "relevance_score": 0.5,
    "is_red_herring": false,
    "notes": "string or null",
    "connections": []
  }
]
```

### Discover Clue

Discovers a new clue in the story.

```http
POST /stories/{story_id}/clues
```

#### Parameters

| Parameter | Type   | Description                    |
|-----------|--------|--------------------------------|
| story_id  | UUID   | The ID of the story           |

#### Request Body

```json
{
  "template_clue_id": "uuid",
  "discovery_method": "string",
  "discovery_location": "string"
}
```

#### Response

```json
{
  "id": "uuid",
  "story_id": "uuid",
  "template_clue_id": "uuid",
  "discovered_at": "ISO8601 datetime",
  "discovery_method": "string",
  "discovery_location": "string",
  "relevance_score": 0.5,
  "is_red_herring": false,
  "notes": null,
  "connections": []
}
```

### Update Clue Notes

Updates the notes for a discovered clue.

```http
PUT /clues/{clue_id}/notes
```

#### Parameters

| Parameter | Type   | Description                    |
|-----------|--------|--------------------------------|
| clue_id   | UUID   | The ID of the clue to update   |

#### Request Body

```json
{
  "notes": "string"
}
```

#### Response

```json
{
  "id": "uuid",
  "notes": "string",
  // ... other clue fields
}
```

### Add Clue Connection

Adds a connection between two clues.

```http
POST /clues/{clue_id}/connections
```

#### Parameters

| Parameter | Type   | Description                    |
|-----------|--------|--------------------------------|
| clue_id   | UUID   | The ID of the source clue      |

#### Request Body

```json
{
  "connected_clue_id": "uuid",
  "connection_type": "string",
  "connection_details": {
    "reason": "string",
    // ... other connection details
  }
}
```

#### Response

```json
{
  "id": "uuid",
  "connections": [
    {
      "connected_clue_id": "uuid",
      "connection_type": "string",
      "details": {
        "reason": "string"
      },
      "created_at": "ISO8601 datetime"
    }
  ]
}
```

### Update Clue Relevance

Updates the relevance score of a clue.

```http
PUT /clues/{clue_id}/relevance
```

#### Parameters

| Parameter | Type   | Description                    |
|-----------|--------|--------------------------------|
| clue_id   | UUID   | The ID of the clue to update   |

#### Request Body

```json
{
  "relevance_score": 0.8
}
```

#### Response

```json
{
  "id": "uuid",
  "relevance_score": 0.8,
  // ... other clue fields
}
```

### Get Clue Connections

Retrieves all connections for a specific clue.

```http
GET /clues/{clue_id}/connections
```

#### Parameters

| Parameter | Type   | Description                    |
|-----------|--------|--------------------------------|
| clue_id   | UUID   | The ID of the clue to query    |

#### Response

```json
[
  {
    "connected_clue_id": "uuid",
    "connection_type": "string",
    "details": {
      "reason": "string"
    },
    "created_at": "ISO8601 datetime"
  }
]
```

### Mark Clue as Red Herring

Marks a clue as a red herring or not.

```http
PUT /clues/{clue_id}/red-herring
```

#### Parameters

| Parameter | Type   | Description                    |
|-----------|--------|--------------------------------|
| clue_id   | UUID   | The ID of the clue to update   |

#### Request Body

```json
{
  "is_red_herring": true
}
```

#### Response

```json
{
  "id": "uuid",
  "is_red_herring": true,
  // ... other clue fields
}
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request

```json
{
  "error": "Missing required fields",
  "required": ["field1", "field2"]
}
```

### 404 Not Found

```json
{
  "error": "Clue not found"
}
```

### 500 Internal Server Error

```json
{
  "error": "Internal server error"
}
```

## Rate Limiting

The API implements rate limiting to prevent abuse. The current limits are:

- 100 requests per minute per IP address
- 1000 requests per hour per user

When rate limits are exceeded, the API will return a 429 Too Many Requests response:

```json
{
  "error": "Rate limit exceeded",
  "retry_after": 60
}
``` 