# Testing Documentation

## Overview
This document outlines the testing strategy, process, and known issues for the Murder Mystery backend.

## Test Types

### 1. Unit Tests
- Location: `backend/tests/unit/`
- Purpose: Test individual components in isolation
- Coverage: Functions, classes, and methods
- Run: `pytest backend/tests/unit`

### 2. Integration Tests
- Location: `backend/tests/integration/`
- Purpose: Test component interactions
- Coverage: API endpoints, database operations
- Run: `pytest backend/tests/integration`

### 3. Edge Case Tests
- Location: `backend/tests/test_edge_cases.py`
- Purpose: Test boundary conditions and error scenarios
- Coverage: Input validation, error handling
- Run: `pytest backend/tests/test_edge_cases.py`

### 4. Load Tests
- Location: `backend/tests/test_load.py`
- Purpose: Test system performance under load
- Coverage: Response times, concurrent users
- Run: `pytest backend/tests/test_load.py`

## Test Coverage
- Minimum coverage requirement: 80%
- Current coverage: [See Codecov report]
- Coverage report generation: `pytest --cov=backend --cov-report=html`

## Known Issues

### 1. Performance
- [ ] High response time for story generation (>2s)
- [ ] Memory usage spikes during concurrent user tests
- [ ] Database connection pool exhaustion under heavy load

### 2. Edge Cases
- [ ] Race conditions in story state updates
- [ ] Inconsistent error messages for validation failures
- [ ] Memory leaks in long-running sessions

### 3. Integration
- [ ] Intermittent failures in Supabase connection
- [ ] Cache invalidation issues
- [ ] WebSocket connection drops

## Test Environment

### Local Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install pytest pytest-cov pytest-xdist
   ```

2. Set up test database:
   ```bash
   createdb test_db
   ```

3. Run tests:
   ```bash
   pytest backend/tests/
   ```

### CI/CD Pipeline
- Tests run automatically on:
  - Pull requests to main branch
  - Pushes to main branch
- Pipeline includes:
  - Unit tests
  - Integration tests
  - Edge case tests
  - Load tests
  - Coverage reporting

## Test Data
- Test fixtures: `backend/tests/fixtures/`
- Mock data: `backend/tests/mocks/`
- Test database: PostgreSQL 13

## Performance Benchmarks
- Response time threshold: <500ms
- Concurrent users: 100
- Memory usage: <1GB
- CPU usage: <50%

## Troubleshooting

### Common Issues
1. Database connection failures
   - Check PostgreSQL service
   - Verify connection string
   - Check network connectivity

2. Test timeouts
   - Increase timeout in pytest.ini
   - Check system resources
   - Review long-running tests

3. Coverage issues
   - Run coverage with --cov-append
   - Check for excluded files
   - Verify test execution

### Debugging
1. Enable verbose output:
   ```bash
   pytest -v backend/tests/
   ```

2. Show print statements:
   ```bash
   pytest -s backend/tests/
   ```

3. Debug specific test:
   ```bash
   pytest backend/tests/test_file.py::test_name -v
   ```

## Maintenance

### Regular Tasks
1. Update test data
2. Review and update benchmarks
3. Clean up old test artifacts
4. Update documentation

### Best Practices
1. Write descriptive test names
2. Keep tests independent
3. Clean up test data
4. Document test dependencies
5. Regular test maintenance

## Contact
For test-related issues or questions:
- Create an issue in the repository
- Tag with 'testing' label
- Assign to the testing team 