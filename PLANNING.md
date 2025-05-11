# Murþrą - Project Planning Document

## 🔍 Project Vision

Murþrą is a personalized, AI-driven detective experience that adapts to the player's psychology and decisions, blending narrative storytelling with a visual investigation interface. The application creates unique murder mysteries tailored to each user's psychological profile and preferences, offering an immersive detective experience through both narrative interaction and a visual investigation board.

## 🏗️ Architecture Overview

### System Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  Vue.js Frontend│◄────┤  Flask Backend  │◄────┤   AI Agents     │
│  (Nuxt.js)      │     │                 │     │   (Archon MCP)  │
│                 │     │                 │     │                 │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                       │
         │                       │                       │
         │                       ▼                       │
         │              ┌─────────────────┐              │
         │              │                 │              │
         └─────────────►│    Supabase     │◄─────────────┘
                        │    (Auth/DB)    │
                        │                 │
                        └────────┬────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │                 │
                        │     Redis       │
                        │  (Cache/Memory) │
                        │                 │
                        └─────────────────┘
```

### Component Architecture

1. **Frontend Layer**
   - Vue.js with Nuxt.js for SSR capabilities
   - Tailwind CSS for styling
   - Pinia for state management
   - Dual interface modes:
     - Narrative Mode (text-based interaction)
     - Detective Board (visual corkboard interface)

2. **Backend Layer**
   - Flask API server
   - Endpoint categories:
     - User management
     - Story generation and progression
     - Clue and evidence management
     - Board state synchronization

3. **AI Layer**
   - Archon MCP for agent orchestration
   - Agent types:
     - StoryAgent: Narrative generation and progression
     - SuspectAgent: Character management and interactions
     - ClueAgent: Evidence generation and connections
     - BoardAgent: Visual board state management
     - CoordinatorAgent: Cross-agent synchronization

4. **Data Layer**
   - Supabase:
     - User authentication and profiles
     - Story templates and progression
     - Mystery state persistence
   - Redis:
     - Agent memory cache
     - LLM response cache
     - Session state management

## 🧠 AI Architecture

### Agent System

The AI system is built on a modular agent architecture using the Archon MCP framework:

1. **StoryAgent**
   - Responsibilities:
     - Generate narrative text based on player actions
     - Maintain story coherence and pacing
     - Adapt narrative tone to player psychology
   - Inputs: Player actions, story state, player profile
   - Outputs: Narrative text, story state updates

2. **SuspectAgent**
   - Responsibilities:
     - Maintain suspect profiles and behaviors
     - Generate dialogue and reactions
     - Manage alibis, motives, and inconsistencies
   - Inputs: Player interactions, story context
   - Outputs: Suspect responses, updated suspect states

3. **ClueAgent**
   - Responsibilities:
     - Generate and place clues based on mystery template
     - Track discovered and undiscovered clues
     - Create logical connections between evidence
   - Inputs: Story state, player actions
   - Outputs: New clues, clue connections, evidence details

4. **BoardAgent**
   - Responsibilities:
     - Synchronize narrative progress with visual board
     - Update visual elements based on discoveries
     - Manage visual connections between elements
   - Inputs: Story state, discovered clues, player board actions
   - Outputs: Board state updates, visual element properties

5. **CoordinatorAgent**
   - Responsibilities:
     - Orchestrate inter-agent communication
     - Maintain global consistency
     - Resolve conflicts between agent outputs
   - Inputs: All agent states and outputs
   - Outputs: Synchronized state updates, conflict resolutions

### Memory System

- **mem0** for persistent memory across sessions
- Memory categories:
  - Facts: Discovered truths about the mystery
  - Interactions: History of character conversations
  - Discoveries: Timeline of clue revelations
  - Player Profile: Psychological traits and preferences

### LLM Integration

- Primary models:
  - Deepseek-r1 or v3 via Openrouter/Together.ai for storytelling
  - Mistral via Openrouter/Together.ai for reasoning and fact-checking
- Integration via Pydantic AI's pluggable LLM interfaces
- Response caching in Supabase and Redis for performance

## 🧩 Mystery Templates

Mystery templates provide structured frameworks that the AI agents populate with dynamic content based on player profiles. Each template includes:

- **Structure**: Murder type, suspect count, clue distribution
- **Logic Hooks**: Constraints on story progression
- **Dynamic Slots**: Placeholders filled based on player profile

Example template structure:
```json
{
  "title": "The Locked Room Mystery",
  "victim": "{{victim_name}}",
  "murder_method": "Blunt force trauma",
  "location": "Private study, locked from the inside",
  "suspects": [
    {
      "name": "{{suspect_1}}",
      "motive": "{{motive_1}}",
      "alibi": "{{alibi_1}}",
      "guilty": true
    },
    {
      "name": "{{suspect_2}}",
      "motive": "{{motive_2}}",
      "alibi": "{{alibi_2}}",
      "guilty": false
    }
  ],
  "clues": [
    {
      "type": "physical",
      "description": "A bloodied candlestick",
      "found_at": "bookshelf",
      "relevance": "murder weapon"
    },
    {
      "type": "logical",
      "description": "The window was unlocked from the outside",
      "relevance": "explains the locked-room trick"
    }
  ],
  "red_herrings": [
    "A torn photo suggesting an affair (unrelated)"
  ]
}
```

## 🛠️ Technology Stack

### Frontend
- **Framework**: Vue.js 3 with Composition API
- **Meta-framework**: Nuxt.js 3
- **State Management**: Pinia
- **Styling**: Tailwind CSS
- **Animations**: GSAP
- **Visual Board**: 
  - Vue Draggable
  - D3.js for connections
  - Custom SVG components

### Backend
- **API Server**: Flask
- **Authentication**: Supabase Auth
- **Database**: Supabase PostgreSQL
- **Caching**: Redis
- **Deployment**: Render

### AI & ML
- **Agent Framework**: Archon MCP
- **LLM Integration**: Pydantic AI
- **Memory System**: mem0
- **Models**: 
  - Deepseek-r1/v3
  - Mistral
- **API Providers**: Openrouter, Together.ai

## 📊 Data Models

### User
```
- id: UUID
- email: String
- password: Hashed String
- profile:
  - psychological_traits: JSON
  - preferences: JSON
  - play_history: JSON
```

### Mystery
```
- id: UUID
- user_id: UUID (FK)
- template_id: UUID (FK)
- title: String
- state: JSON
- created_at: Timestamp
- updated_at: Timestamp
```

### Story
```
- id: UUID
- mystery_id: UUID (FK)
- current_scene: String
- narrative_history: JSON
- discovered_clues: JSON
- suspect_states: JSON
```

### Board
```
- id: UUID
- mystery_id: UUID (FK)
- elements: JSON
- connections: JSON
- notes: JSON
- layout: JSON
```

## 🔐 Security Considerations

1. **Authentication**
   - JWT-based auth via Supabase
   - Secure password storage
   - Rate limiting on auth endpoints

2. **Data Protection**
   - Encryption of sensitive user data
   - Regular backups of user stories
   - Privacy-focused data retention policies

3. **API Security**
   - HTTPS for all communications
   - API key management for LLM services
   - Input validation and sanitization

## 📱 Responsive Design

The application will be responsive across devices:

1. **Desktop**: Full experience with side-by-side narrative and board views
2. **Tablet**: Tabbed interface switching between narrative and board
3. **Mobile**: Optimized vertical scrolling with collapsible sections

## 🧪 Testing Strategy

1. **Unit Testing**
   - Vue components with Vue Test Utils
   - Python backend with pytest
   - Agent logic with mock LLM responses

2. **Integration Testing**
   - API endpoint testing
   - Agent interaction testing
   - Frontend-backend communication

3. **User Testing**
   - Narrative coherence evaluation
   - Mystery solvability testing
   - UX feedback collection

## 📈 Performance Considerations

1. **LLM Response Caching**
   - Cache common LLM responses
   - Implement progressive loading for narrative

2. **Optimized Board Rendering**
   - Virtual scrolling for large boards
   - Lazy loading of visual elements
   - Efficient SVG rendering

3. **Backend Optimization**
   - Asynchronous processing where possible
   - Efficient database queries
   - Horizontal scaling capability

## 🚀 Deployment Strategy

1. **Development Environment**
   - Local development with Docker
   - CI/CD with GitHub Actions

2. **Staging Environment**
   - Render preview deployments
   - Integration testing

3. **Production Environment**
   - Render web service
   - Supabase production instance
   - Redis Cloud for caching

## 📝 Coding Standards

1. **Frontend**
   - Vue.js style guide (Priority A rules)
   - Component-based architecture
   - TypeScript for type safety

2. **Backend**
   - PEP 8 for Python code
   - RESTful API design principles
   - Comprehensive docstrings

3. **General**
   - Git flow branching strategy
   - Semantic versioning
   - Comprehensive documentation

## 🔄 Iteration Plan

The project will follow an iterative development approach:

1. **MVP (Minimum Viable Product)**
   - Basic user authentication
   - Single mystery template
   - Text-only narrative interface
   - Simple visual board

2. **Alpha Release**
   - Multiple mystery templates
   - Basic psychological profiling
   - Enhanced narrative capabilities
   - Interactive visual board

3. **Beta Release**
   - Full psychological profiling
   - Advanced agent interactions
   - Complete visual board functionality
   - Performance optimizations

4. **Production Release**
   - Polished UI/UX
   - Comprehensive mystery library
   - Advanced AI capabilities
   - Mobile responsiveness