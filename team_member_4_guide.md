# Team Member 4 - Milestone 3 Task Guide

## Your Tasks Overview

| Task ID | Title | Estimate | Dependencies |
|---------|-------|----------|-------------|
| AI-009 | Implement psychological profiling logic | 8h | AI-002 |
| DB-004 | Design and implement board state schema | 4h | DB-003 |
| TEST-005 | Create end-to-end testing suite | 8h | FE-005, BE-005 |
| **Total** | | **20h** | |

## Task Details and Implementation Guide

### AI-009: Implement psychological profiling logic

#### Description
Develop logic for analyzing and applying player psychological profiles. Integrate this logic with StoryAgent and SuspectAgent to adapt the narrative and character interactions to the player's traits.

#### Implementation Steps

1. **Review player profile data model and agent integration**
   - Examine how psychological traits are stored and accessed.
   - Review StoryAgent and SuspectAgent code for integration points.

2. **Design profiling logic**
   - Define how traits influence narrative tone, choices, and suspect behavior.
   - Plan for extensibility and future trait additions.

3. **Implement profiling logic in agents**
   - Add methods to analyze and apply traits in StoryAgent and SuspectAgent.
   - Ensure logic is testable and well-documented.

4. **Write unit tests for profiling logic**
   ```bash
   # Create test file
   touch backend/tests/test_psychological_profiling.py
   ```

5. **Document profiling logic and integration points**
   - Update code comments and project documentation.

#### Resources
- [Pydantic Documentation](https://docs.pydantic.dev/latest/)
- [Python Testing (pytest)](https://docs.pytest.org/)
- [AI Agent Design](https://github.com/pydantic/pydanticai)

---

### DB-004: Design and implement board state schema

#### Description
Design and implement the Supabase schema for detective board state persistence. This ensures that board layouts, elements, and connections are saved and restored for each user and mystery.

#### Implementation Steps

1. **Review current board data model and requirements**
   - Examine frontend and backend expectations for board state.
   - Identify all fields and relationships needed.

2. **Design Supabase schema**
   - Plan tables for elements, connections, notes, and layouts.
   - Define primary/foreign keys and indexes.

3. **Implement schema in Supabase**
   - Use SQL editor or migration scripts to create tables.
   - Set up RLS (Row Level Security) policies for user data protection.

4. **Document schema and relationships**
   - Create ERD (Entity Relationship Diagram) and add table/column comments.

5. **Write migration and rollback scripts**
   - Ensure schema changes are version-controlled and reversible.

#### Resources
- [Supabase Documentation](https://supabase.com/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Database Schema Design Best Practices](https://www.postgresql.org/docs/current/ddl.html)

---

### TEST-005: Create end-to-end testing suite

#### Description
Develop an end-to-end (E2E) testing suite covering major user journeys, from login to solving a mystery. Use Cypress or a similar tool for frontend E2E tests and integrate with CI for automated testing.

#### Implementation Steps

1. **Review major user flows and UI components**
   - Identify critical paths (e.g., login, board interaction, suspect dialogue).
   - Review existing E2E and integration tests.

2. **Set up Cypress or similar E2E framework**
   ```bash
   # Install Cypress
   npm install --save-dev cypress
   # Create E2E test directory
   mkdir -p frontend/cypress/e2e
   ```

3. **Write E2E test scripts**
   ```bash
   # Create test files
   touch frontend/cypress/e2e/board.cy.js
   touch frontend/cypress/e2e/suspect.cy.js
   # ...etc.
   ```
   - Cover expected, edge, and failure cases for each flow.

4. **Integrate with CI**
   - Ensure E2E tests run automatically in GitHub Actions or your CI pipeline.

5. **Document test coverage and results**
   - Update documentation with test scenarios and outcomes.

#### Resources
- [Cypress Documentation](https://docs.cypress.io/)
- [Testing Vue Applications](https://vuejs.org/guide/scaling-up/testing.html)
- [GitHub Actions for CI/CD](https://docs.github.com/en/actions)

---

## Testing Your Work

- Run the backend and frontend development servers.
- Test all profiling, schema, and E2E features.
- Write and run unit/E2E tests for all new code.
- Verify security and data integrity for board state.

## Communication

If you encounter any blockers or have questions:
- Post in the #milestone-3 Slack channel
- Tag the project lead for urgent issues
- Document any design decisions or assumptions in your PR description

Good luck with your tasks! Remember to commit your work regularly and create pull requests for review.

---

*This guide will be updated as Milestone 3 progresses. Good luck!*