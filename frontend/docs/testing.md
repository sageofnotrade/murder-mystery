# Frontend Testing Documentation

## Overview
This project uses Cypress for end-to-end testing and Percy for visual regression testing. The testing suite covers authentication, game flow, and suspect interactions.

## Setup
1. Install dependencies:
```bash
npm install
```

2. Set up Percy:
- Get your Percy token from the Percy dashboard
- Set the token in your environment:
```bash
export PERCY_TOKEN=your_token_here
```

## Running Tests
1. Start the development server:
```bash
npm run dev
```

2. Run Cypress tests:
```bash
npm run cypress:open  # Opens Cypress UI
# or
npm run cypress:run  # Runs tests headlessly
```

3. Run visual regression tests:
```bash
npm run percy:test
```

## Test Structure
- `cypress/e2e/auth.cy.ts`: Authentication tests
- `cypress/e2e/game.cy.ts`: Game flow tests
- `cypress/e2e/suspect.cy.ts`: Suspect interaction tests

## Visual Regression Testing
Percy snapshots are taken at key points in the user journey:
- Login/Registration forms
- Game creation and details
- Suspect interactions
- Clue discovery

## CI Integration
Tests run automatically on:
- Pull requests
- Main branch merges
- Daily scheduled runs

## Known Issues
1. Visual tests may fail due to dynamic content
2. Some tests require backend services to be running
3. Time-dependent tests may need adjustment

## Best Practices
1. Use data-test attributes for selectors
2. Keep tests independent
3. Clean up test data after each test
4. Use meaningful snapshot names 