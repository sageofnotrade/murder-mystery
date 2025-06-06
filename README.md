# Murder Mystery

... (existing content) ...

## End-to-End (E2E) Tests

E2E tests (Cypress) cover major user flows, deployment health, error boundaries, and UI polish. Specs live in `frontend/cypress/e2e/`.

### Running E2E Tests

- Local: `cd frontend && npx cypress run`
- Headed: `npx cypress open`
- Against staging/production: Set `CYPRESS_baseUrl` or edit `deployment.cy.js` URLs.

### What’s Covered
- Detective board interactions
- Game flow
- Suspect interactions
- Deployment health (local, staging, prod)
- Error boundaries & network failures
- Responsive/mobile UI

See comments in each test file for details.

## Integration Tests

Integration tests cover major user flows between the frontend and backend, using mocks for external dependencies (LLM, Supabase, Redis). These tests live in `backend/tests/` and use the Flask test client.

### Running Integration Tests

To run a specific integration test (e.g., board state sync):

```
python -m pytest backend/tests/test_integration_board.py -v
python -m pytest backend/tests/test_integration_story.py -v
python -m pytest backend/tests/test_integration_clue.py -v
python -m pytest backend/tests/test_integration_auth.py -v
```

### What’s Covered
- Board state synchronization (save/load)
- Story progression
- Clue management
- Authentication flows

Mocks for Supabase and Redis are provided in `backend/tests/mocks/`.

---

For more details, see comments in each test file.
