# Team Member 1 - Milestone 3 Task Guide

## Your Tasks Overview

| Task ID | Title | Estimate | Dependencies |
|---------|-------|----------|-------------|
| FE-007 | Create draggable elements for detective board | 6h | FE-006 |
| FE-009 | Develop UI for suspect profiles | 4h | FE-003 |
| BE-007 | Create suspect interaction endpoints | 6h | BE-005 |
| **Total** | | **16h** | |

## Task Details and Implementation Guide

### FE-007: Create draggable elements for detective board

#### Description
Implement draggable Vue components for suspects, clues, locations, and notes on the detective board. This will allow users to visually organize and connect elements as part of their investigation.

#### Implementation Steps

1. **Review existing detective board UI (FE-006)**
   - Examine the current board structure and element rendering.
   - Note the use of libraries (e.g., Vue Draggable, D3.js).

2. **Design draggable element components**
   - Plan for separate components for suspects, clues, locations, and notes.
   - Ensure each component supports drag-and-drop and displays relevant data.

3. **Implement Vue components**
   ```bash
   # Create draggable element components
   touch frontend/components/board/SuspectElement.vue
   touch frontend/components/board/ClueElement.vue
   touch frontend/components/board/LocationElement.vue
   touch frontend/components/board/NoteElement.vue
   ```

4. **Integrate with board state**
   - Use Pinia store for managing element positions and state.
   - Ensure state persistence on drag events.

5. **Add drag-and-drop functionality**
   - Use `vuedraggable` for drag-and-drop.
   - Implement event handlers for drag start, drag end, and drop.

6. **Ensure responsive design**
   - Test drag-and-drop on desktop, tablet, and mobile.
   - Adjust hitboxes and touch support as needed.

7. **Write unit/component tests**
   ```bash
   # Create test files
   touch frontend/tests/components/SuspectElement.spec.js
   touch frontend/tests/components/ClueElement.spec.js
   # ...etc.
   ```

#### Resources
- [Vue Draggable](https://github.com/SortableJS/vue.draggable.next)
- [Pinia State Management](https://pinia.vuejs.org/core-concepts/)
- [Vue.js Composition API](https://vuejs.org/guide/introduction.html)
- [Testing Vue Components](https://test-utils.vuejs.org/)

---

### FE-009: Develop UI for suspect profiles

#### Description
Design and implement Vue components for displaying and editing suspect profiles, including their details, alibis, motives, and psychological traits.

#### Implementation Steps

1. **Review suspect data structure**
   - Check backend API and data models for suspect information.
   - Identify required fields for display and editing.

2. **Design suspect profile components**
   - Plan for a main profile view and editable fields.
   - Include sections for alibi, motive, and psychological traits.

3. **Implement Vue components**
   ```bash
   # Create suspect profile components
   touch frontend/components/board/SuspectProfile.vue
   touch frontend/components/board/SuspectTraitList.vue
   ```

4. **Integrate with backend endpoints**
   - Use API service to fetch and update suspect data.
   - Handle loading, error, and success states.

5. **Ensure accessibility and responsive layout**
   - Use semantic HTML and ARIA attributes.
   - Test on various screen sizes.

6. **Write unit/component tests**
   ```bash
   # Create test files
   touch frontend/tests/components/SuspectProfile.spec.js
   ```

#### Resources
- [Vue.js Forms Guide](https://vuejs.org/guide/essentials/forms.html)
- [Tailwind CSS](https://tailwindcss.com/docs/)
- [Accessibility in Vue](https://vuejs.org/guide/best-practices/accessibility.html)

---

### BE-007: Create suspect interaction endpoints

#### Description
Implement Flask API endpoints for suspect interactions, such as dialogue, alibi verification, and motive exploration. Integrate with the SuspectAgent for dynamic responses.

#### Implementation Steps

1. **Review SuspectAgent and story progression endpoints**
   - Understand how suspect data is managed and updated.
   - Review existing agent logic for dialogue and state.

2. **Design API endpoints**
   - Plan endpoints for getting/setting suspect data, posting dialogue, and verifying alibis.
   - Define request/response formats.

3. **Implement Flask routes**
   ```bash
   # Create suspect routes file
   touch backend/routes/suspect_routes.py
   ```

4. **Integrate with SuspectAgent**
   - Connect endpoints to SuspectAgent logic for dynamic responses.
   - Handle error and edge cases.

5. **Add authentication and authorization**
   - Use JWT or session-based auth for protected endpoints.

6. **Write unit tests**
   ```bash
   # Create test file
   touch backend/tests/test_suspect_routes.py
   ```

#### Example API Endpoints

```
GET /api/suspects/{id} - Get suspect profile
POST /api/suspects/{id}/dialogue - Post dialogue and get response
POST /api/suspects/{id}/verify-alibi - Verify suspect alibi
```

#### Resources
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/latest/)
- [RESTful API Design](https://restfulapi.net/)
- [Testing Flask Apps](https://flask.palletsprojects.com/en/2.0.x/testing/)

---

## Testing Your Work

- Run the frontend and backend development servers.
- Test all drag-and-drop, suspect profile, and interaction features.
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