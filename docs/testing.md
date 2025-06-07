# Testing Documentation

## Overview
This document outlines our testing strategy, coverage requirements, and best practices for the Murder Mystery application.

## Test Types

### 1. Unit Tests
- [ ] Backend API endpoints
- [ ] Utility functions
- [ ] State management
- [ ] Helper functions

### 2. Integration Tests
- [ ] API integration
- [ ] Database operations
- [ ] Authentication flow
- [ ] State management integration

### 3. E2E Tests (Cypress)
- [ ] Authentication
  - [ ] Login
  - [ ] Registration
  - [ ] Password reset
  - [ ] Session management
- [ ] Game Management
  - [ ] Create new game
  - [ ] Edit game details
  - [ ] Delete game
  - [ ] Game state transitions
- [ ] Suspect Management
  - [ ] Add suspect
  - [ ] Edit suspect details
  - [ ] Remove suspect
  - [ ] Suspect questioning
- [ ] Clue Management
  - [ ] Add clue
  - [ ] Edit clue
  - [ ] Connect clues
  - [ ] Clue analysis
- [ ] Board Interactions
  - [ ] Drag and drop
  - [ ] Connection creation
  - [ ] Element resizing
  - [ ] Board navigation

### 4. Visual Tests (Percy)
- [ ] Authentication pages
- [ ] Game board
- [ ] Suspect profiles
- [ ] Clue details
- [ ] Responsive layouts
- [ ] Dark/Light themes

## Test Coverage Requirements

### Minimum Coverage Thresholds
- Unit Tests: 80%
- Integration Tests: 70%
- E2E Tests: Critical paths only
- Visual Tests: All UI components

### Critical Paths
1. User Authentication
2. Game Creation
3. Suspect Management
4. Clue Management
5. Board Interactions

## Running Tests

### Local Development
```bash
# Run all tests
npm test

# Run specific test types
npm run test:unit
npm run test:integration
npm run test:e2e
npm run test:visual

# Run Cypress in interactive mode
npm run cypress:open
```

### CI/CD Pipeline
Tests run automatically on:
- Pull requests
- Merges to main branch
- Nightly builds

## Best Practices

### Writing Tests
1. Follow AAA pattern (Arrange, Act, Assert)
2. Use meaningful test descriptions
3. Keep tests independent
4. Clean up after tests
5. Use appropriate waiting strategies

### Cypress Specific
1. Use data-cy attributes for selectors
2. Handle async operations properly
3. Use custom commands for common operations
4. Implement proper error handling
5. Take visual snapshots at key points

### Visual Testing
1. Capture snapshots of all major UI states
2. Test responsive layouts
3. Include error states
4. Test loading states
5. Verify accessibility

## Debugging Tests

### Common Issues
1. Timing issues
   - Use proper waiting strategies
   - Avoid arbitrary timeouts
2. Selector issues
   - Use data-cy attributes
   - Avoid brittle selectors
3. State management
   - Reset state between tests
   - Use proper setup/teardown

### Debugging Tools
1. Cypress Test Runner
2. Percy Visual Review
3. Browser DevTools
4. Network tab monitoring

## Maintenance

### Regular Tasks
1. Update test dependencies
2. Review and update snapshots
3. Clean up old test data
4. Monitor test performance
5. Update documentation

### Review Process
1. Code review includes test review
2. Verify test coverage
3. Check for flaky tests
4. Review visual changes
5. Update documentation

## Resources
- [Cypress Documentation](https://docs.cypress.io)
- [Percy Documentation](https://docs.percy.io)
- [Testing Best Practices](https://docs.cypress.io/guides/references/best-practices)
- [Visual Testing Guide](https://docs.percy.io/docs/visual-testing) 