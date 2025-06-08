# TASKS

## Completed
- TEST-004: Develop Integration Tests for Frontend-Backend (board, story, clue, auth test scaffolds) — 2024-06-07
- AI-010: Advanced agent tuning & prompt engineering — 2024-06-08
  - All agent prompt/model strategies refactored and documented for clarity, performance, and maintainability.
- TEST-011: Patch StoryAgent test setup error by adding dummy mem0 for patching — 2024-06-09
    - Added `mem0 = None` to backend/agents/story_agent.py to allow tests to patch mem0 without AttributeError.

## In Progress

- TEST-008: End-to-end polish & deployment testing — 2024-06-09 (COMPLETED)

## Discovered During Work
- Add/maintain E2E deployment health and error boundary tests for all environments
- Ensure E2E tests run in CI for all major branches
- Document E2E test usage and environment config in README.md
- Expand integration tests for story progression, clue management, and authentication flows
- Ensure all integration tests are included in CI
- Document integration test usage in README.md
- Review and update agent-specific documentation to reflect new prompt/model strategies
- [x] Stabilize integration auth tests: mock Supabase, fix client usage, update assertions (2024-06-09)
- [ ] Ensure all other integration tests (story, template, clue, suspect, user_progress) are fully mocked and passing
- [x] Fix and stabilize LLM caching tests (backend/tests/test_llm_caching.py) - 2024-06-10
- [ ] SQL validation test fails due to missing file: database/board_state_schema.sql
