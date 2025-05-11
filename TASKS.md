# Murþrą - Project Tasks

## 📋 Task Tracking System

This document tracks all current tasks, backlog items, and sub-tasks for the Murþrą project. Each task includes:

- **ID**: Unique identifier (e.g., FE-001 for Frontend tasks)
- **Title**: Brief description
- **Status**: Not Started | In Progress | Blocked | Completed
- **Priority**: High | Medium | Low
- **Estimate**: Time estimate in hours or story points
- **Assignee**: Person responsible (if applicable)
- **Dependencies**: IDs of tasks that must be completed first
- **Sub-tasks**: Smaller units of work

## 🚀 Current Sprint Tasks

### Project Setup

| ID | Title | Status | Priority | Estimate | Assignee | Dependencies |
|----|-------|--------|----------|----------|----------|-------------|
| SETUP-001 | Initialize Git repository | Completed | High | 1h | - | - |
| SETUP-002 | Create project documentation (README, PLANNING, TASKS) | Completed | High | 3h | - | SETUP-001 |
| SETUP-003 | Set up Supabase project | In Progress | High | 2h | You | - |
| SETUP-004 | Configure Redis instance | In Progress | Medium | 2h | You | - |
| SETUP-005 | Set up development environment | In Progress | High | 4h | You | - |

### Frontend Tasks

| ID | Title | Status | Priority | Estimate | Assignee | Dependencies |
|----|-------|--------|----------|----------|----------|-------------|
| FE-001 | Initialize Vue.js/Nuxt.js project | Not Started | High | 2h | Team Member 1 | SETUP-005 |
| FE-002 | Set up Tailwind CSS | Not Started | High | 1h | Team Member 2 | FE-001 |
| FE-003 | Implement authentication UI | Not Started | High | 4h | Team Member 3 | FE-001, FE-002 |
| FE-004 | Create psychological profile questionnaire UI | Not Started | Medium | 6h | - | FE-003 |
| FE-005 | Develop narrative interface component | Not Started | High | 8h | - | FE-003 |
| FE-006 | Implement basic detective board UI | Not Started | High | 10h | - | FE-003 |
| FE-007 | Create draggable elements for detective board | Not Started | Medium | 6h | - | FE-006 |
| FE-008 | Implement connection visualization between board elements | Not Started | Medium | 8h | - | FE-007 |
| FE-009 | Develop UI for suspect profiles | Not Started | Medium | 4h | - | FE-003 |
| FE-010 | Create clue detail view components | Not Started | Medium | 4h | - | FE-003 |

### Backend Tasks

| ID | Title | Status | Priority | Estimate | Assignee | Dependencies |
|----|-------|--------|----------|----------|----------|-------------|
| BE-001 | Initialize Flask project | Not Started | High | 2h | Team Member 1 | SETUP-005 |
| BE-002 | Set up Supabase authentication integration | Not Started | High | 4h | Team Member 2 | BE-001, SETUP-003 |
| BE-003 | Implement user profile endpoints | Not Started | High | 4h | Team Member 3 | BE-002 |
| BE-004 | Create mystery template storage and retrieval | Not Started | High | 6h | - | BE-001 |
| BE-005 | Develop story progression endpoints | Not Started | High | 8h | - | BE-004 |
| BE-006 | Implement clue management API | Not Started | Medium | 6h | - | BE-005 |
| BE-007 | Create suspect interaction endpoints | Not Started | Medium | 6h | - | BE-005 |
| BE-008 | Develop board state synchronization API | Not Started | Medium | 8h | - | BE-006, BE-007 |
| BE-009 | Implement Redis caching for LLM responses | Not Started | Low | 4h | - | BE-005, SETUP-004 |
| BE-010 | Create user progress saving/loading endpoints | Not Started | Medium | 4h | - | BE-005 |

### AI Agent Tasks

| ID | Title | Status | Priority | Estimate | Assignee | Dependencies |
|----|-------|--------|----------|----------|----------|-------------|
| AI-001 | Set up Archon MCP framework | Not Started | High | 8h | Team Member 4 | BE-001 |
| AI-002 | Implement StoryAgent with Pydantic models | Not Started | High | 10h | - | AI-001 |
| AI-003 | Develop SuspectAgent with personality modeling | Not Started | Medium | 8h | - | AI-001 |
| AI-004 | Create ClueAgent with evidence generation | Not Started | Medium | 8h | - | AI-001 |
| AI-005 | Implement BoardAgent for visual state management | Not Started | Medium | 6h | - | AI-001 |
| AI-006 | Develop CoordinatorAgent for cross-agent communication | Not Started | High | 10h | - | AI-002, AI-003, AI-004, AI-005 |
| AI-007 | Integrate mem0 for persistent memory | Not Started | Medium | 6h | - | AI-001 |
| AI-008 | Set up LLM API integration (Openrouter/Together.ai) | Not Started | High | 4h | - | AI-001 |
| AI-009 | Implement psychological profiling logic | Not Started | Medium | 8h | - | AI-002 |
| AI-010 | Create mystery template parser and populator | Not Started | High | 6h | - | AI-001 |

### Database Tasks

| ID | Title | Status | Priority | Estimate | Assignee | Dependencies |
|----|-------|--------|----------|----------|----------|-------------|
| DB-001 | Design and create user schema in Supabase | Not Started | High | 3h | Team Member 1 | SETUP-003 |
| DB-002 | Implement mystery template schema | Not Started | High | 3h | Team Member 4 | SETUP-003 |
| DB-003 | Create story state storage schema | Not Started | High | 4h | - | DB-002 |
| DB-004 | Design and implement board state schema | Not Started | Medium | 4h | - | DB-003 |
| DB-005 | Set up Redis schema for caching | Not Started | Medium | 3h | - | SETUP-004 |

### Testing Tasks

| ID | Title | Status | Priority | Estimate | Assignee | Dependencies |
|----|-------|--------|----------|----------|----------|-------------|
| TEST-001 | Set up frontend testing framework | Not Started | Medium | 3h | Team Member 1 | FE-001 |
| TEST-002 | Create backend unit tests | Not Started | Medium | 6h | Team Member 2 | BE-001 |
| TEST-003 | Implement AI agent unit tests | Not Started | Medium | 8h | - | AI-001 |
| TEST-004 | Develop integration tests for frontend-backend | Not Started | Medium | 6h | - | FE-005, BE-005 |
| TEST-005 | Create end-to-end testing suite | Not Started | Low | 8h | - | FE-005, BE-005 |

### Deployment Tasks

| ID | Title | Status | Priority | Estimate | Assignee | Dependencies |
|----|-------|--------|----------|----------|----------|-------------|
| DEPLOY-001 | Set up CI/CD pipeline with GitHub Actions | Not Started | Low | 4h | Team Member 3 | SETUP-001 |
| DEPLOY-002 | Configure Render deployment for backend | Not Started | Low | 3h | - | BE-001 |
| DEPLOY-003 | Set up frontend deployment | Not Started | Low | 3h | - | FE-001 |
| DEPLOY-004 | Configure production database | Not Started | Low | 2h | - | DB-001, DB-002, DB-003, DB-004 |

## 📚 Backlog

### Frontend Backlog

| ID | Title | Priority | Estimate | Dependencies |
|----|-------|----------|----------|-------------|
| FE-B001 | Implement advanced board visualization features | Low | 12h | FE-008 |
| FE-B002 | Create mobile-responsive design | Medium | 16h | FE-005, FE-006 |
| FE-B003 | Add animations for narrative transitions | Low | 8h | FE-005 |
| FE-B004 | Implement theme customization | Low | 6h | FE-002 |
| FE-B005 | Create tutorial overlay for new users | Low | 8h | FE-005, FE-006 |

### Backend Backlog

| ID | Title | Priority | Estimate | Dependencies |
|----|-------|----------|----------|-------------|
| BE-B001 | Implement analytics tracking | Low | 8h | BE-003 |
| BE-B002 | Add social sharing functionality | Low | 6h | BE-010 |
| BE-B003 | Create mystery rating system | Low | 4h | BE-010 |
| BE-B004 | Implement performance optimization for large mysteries | Low | 10h | BE-005 |
| BE-B005 | Add webhook support for external integrations | Low | 6h | BE-001 |

### AI Agent Backlog

| ID | Title | Priority | Estimate | Dependencies |
|----|-------|----------|----------|-------------|
| AI-B001 | Implement advanced narrative branching | Low | 12h | AI-002 |
| AI-B002 | Add emotional intelligence to character interactions | Low | 10h | AI-003 |
| AI-B003 | Create dynamic difficulty adjustment based on player performance | Low | 8h | AI-006 |
| AI-B004 | Implement multi-language support | Low | 8h | AI-002 |
| AI-B005 | Add voice narration capabilities | Low | 10h | AI-002 |

## 🔍 Sub-Tasks

### FE-005: Develop narrative interface component

- [ ] FE-005.1: Create basic text display component
- [ ] FE-005.2: Implement user input field for narrative actions
- [ ] FE-005.3: Add action suggestion buttons
- [ ] FE-005.4: Create narrative history scrollback feature
- [ ] FE-005.5: Implement loading states for narrative generation

### BE-005: Develop story progression endpoints

- [ ] BE-005.1: Create endpoint for starting new story
- [ ] BE-005.2: Implement action processing endpoint
- [ ] BE-005.3: Add narrative generation endpoint
- [ ] BE-005.4: Create story state retrieval endpoint
- [ ] BE-005.5: Implement story saving endpoint

### AI-002: Implement StoryAgent with Pydantic models

- [ ] AI-002.1: Define Pydantic models for story structure
- [ ] AI-002.2: Create narrative generation functions
- [ ] AI-002.3: Implement action processing logic
- [ ] AI-002.4: Add story state management
- [ ] AI-002.5: Create prompt templates for LLM integration

## 📅 Milestone Plan

### Milestone 1: Project Foundation (2 weeks)
- Complete all SETUP tasks
- Complete FE-001 through FE-003
- Complete BE-001 through BE-003
- Complete DB-001
- Complete AI-001

### Milestone 2: Basic Functionality (4 weeks)
- Complete FE-004 through FE-006
- Complete BE-004 through BE-006
- Complete DB-002 and DB-003
- Complete AI-002, AI-003, AI-008, AI-010

### Milestone 3: Core Experience (6 weeks)
- Complete all remaining Frontend tasks
- Complete all remaining Backend tasks
- Complete all remaining Database tasks
- Complete all remaining AI Agent tasks
- Complete TEST-001 through TEST-003

### Milestone 4: Polish and Deploy (2 weeks)
- Complete all Testing tasks
- Complete all Deployment tasks
- Address high-priority backlog items

## 📝 Notes and Decisions

- **2023-05-01**: Decided to use Vue.js over React for frontend due to better integration with the planned architecture
- **2023-05-02**: Selected Supabase for authentication and database to simplify backend development
- **2023-05-03**: Chose to implement the detective board using D3.js for better visualization capabilities

## 🔄 Task Updates

This section will be updated as tasks are completed or modified:

- **2023-05-01**: Completed SETUP-001 - Initialized Git repository
- **2023-05-04**: Completed SETUP-002 - Created project documentation
- **2023-05-10**: In Progress SETUP-003, SETUP-004, SETUP-005 - Setting up Supabase, Redis, and development environment
  - Created frontend structure with Vue.js/Nuxt.js
  - Created backend structure with Flask
  - Set up basic authentication with Supabase
  - Created database schema for Supabase
  - Set up environment configuration