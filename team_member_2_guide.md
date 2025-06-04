# Team Member 2 - Milestone 3 Task Guide

## Your Tasks Overview

| Task ID | Title | Estimate | Dependencies |
|---------|-------|----------|-------------|
| FE-008 | Implement connection visualization between board elements | 8h | FE-007 |
| FE-010 | Create clue detail view components | 4h | FE-003 |
| TEST-003 | Implement AI agent unit tests | 8h | AI-001 |
| **Total** | | **20h** | |

## Task Details and Implementation Guide

### FE-008: Implement connection visualization between board elements

#### Description
Use D3.js or SVG to visually connect board elements (suspects, clues, etc.) on the detective board. This will allow users to see relationships and logical links between elements as part of their investigation.

#### Implementation Steps

1. **Review detective board structure (FE-006, FE-007)**
   - Examine how board elements are rendered and positioned.
   - Identify where and how connections should be drawn.

2. **Design connection data model**
   - Define how connections are represented in the Pinia store (e.g., source, target, type).

3. **Implement SVG/D3.js connection rendering**
   ```bash
   # Create connection component
   touch frontend/components/board/ElementConnection.vue
   ```
   - Use SVG lines or D3.js to draw connections between elements.
   - Ensure connections update dynamically as elements are moved.

4. **Add interaction features**
   - Allow users to create and delete connections via UI controls.
   - Implement hover and selection states for connections.

5. **Ensure responsive and accessible design**
   - Test on various screen sizes and input types.
   - Use appropriate ARIA attributes for accessibility.

6. **Write unit/component tests**
   ```bash
   # Create test file
   touch frontend/tests/components/ElementConnection.spec.js
   ```

#### Resources
- [D3.js Documentation](https://d3js.org/)
- [SVG in Vue.js](https://vuejs.org/guide/extras/rendering-mechanism.html#rendering-pipeline)
- [Pinia State Management](https://pinia.vuejs.org/core-concepts/)
- [Testing Vue Components](https://test-utils.vuejs.org/)

---

### FE-010: Create clue detail view components

#### Description
Design and implement Vue components for displaying detailed information about clues, including their description, location, related suspects, and discovery context.

#### Implementation Steps

1. **Review clue data structure**
   - Check backend API and data models for clue information.
   - Identify required fields for display.

2. **Design clue detail components**
   - Plan for a main detail view and supporting subcomponents (e.g., related suspects, discovery context).

3. **Implement Vue components**
   ```bash
   # Create clue detail components
   touch frontend/components/board/ClueDetail.vue
   touch frontend/components/board/ClueRelatedSuspects.vue
   ```

4. **Integrate with backend endpoints**
   - Use API service to fetch clue data.
   - Handle loading, error, and success states.

5. **Ensure responsive and accessible UI**
   - Use semantic HTML and ARIA attributes.
   - Test on various screen sizes.

6. **Write unit/component tests**
   ```bash
   # Create test file
   touch frontend/tests/components/ClueDetail.spec.js
   ```

#### Resources
- [Vue.js Forms Guide](https://vuejs.org/guide/essentials/forms.html)
- [Tailwind CSS](https://tailwindcss.com/docs/)
- [Accessibility in Vue](https://vuejs.org/guide/best-practices/accessibility.html)

---

### TEST-003: Implement AI agent unit tests

#### Description
Write unit tests for all AI agent logic (StoryAgent, SuspectAgent, etc.) in the backend. Use mocks for LLM and database interactions. Integrate with CI for automated testing.

#### Implementation Steps

1. **Review AI agent codebase (backend/agents/)**
   - Identify key methods and logic to test for each agent.
   - Review existing test files and coverage.

2. **Set up test configuration**
   ```bash
   # Ensure pytest and related packages are installed
   pip install pytest pytest-cov
   ```

3. **Create/expand test files**
   ```bash
   # Create or update test files for each agent
   touch backend/tests/test_story_agent.py
   touch backend/tests/test_suspect_agent.py
   touch backend/tests/test_clue_agent.py
   # ...etc.
   ```

4. **Use mocks for LLM/database**
   - Mock LLM API calls and database interactions for isolated testing.

5. **Write tests for expected, edge, and failure cases**
   - Cover all major agent behaviors and error handling.

6. **Integrate with CI**
   - Ensure tests run automatically in GitHub Actions or your CI pipeline.

#### Resources
- [Pytest Documentation](https://docs.pytest.org/)
- [Mocking in Python](https://docs.python.org/3/library/unittest.mock.html)
- [Testing Flask Apps](https://flask.palletsprojects.com/en/2.0.x/testing/)
- [GitHub Actions for CI/CD](https://docs.github.com/en/actions)

---

## Testing Your Work

- Run the frontend and backend development servers.
- Test all connection, clue detail, and agent logic features.
- Write and run unit/component/API tests for all new code.
- Verify mobile responsiveness and accessibility.

## Communication

If you encounter any blockers or have questions:
- Post in the #milestone-3 Slack channel
- Tag the project lead for urgent issues
- Document any design decisions or assumptions in your PR description

Good luck with your tasks! Remember to commit your work regularly and create pull requests for review.

---

*This guide will be updated as Milestone 3 progresses. Good luck!*