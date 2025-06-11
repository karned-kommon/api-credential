# Testing API Credential

This directory contains unit tests for the API Credential service.

## Setup

Install the development dependencies:

```bash
pip install -r requirements.txt
```

## Running Tests

To run all tests:

```bash
pytest
```

To run tests with verbose output:

```bash
pytest -v
```

## Measuring Code Coverage

To run tests with coverage reporting:

```bash
pytest --cov=. --cov-report=term
```

This will show the coverage percentage for each module in the terminal.

For a more detailed HTML report:

```bash
pytest --cov=. --cov-report=html
```

This will generate an HTML report in the `htmlcov` directory. Open `htmlcov/index.html` in a browser to view the report.

## Test Structure

The tests are organized by component:

- `test_items_service.py`: Tests for the secret management service
- `test_licence_middleware.py`: Tests for the license verification middleware
- `test_v1_router.py`: Tests for the API endpoints

Each test file contains test cases that verify the functionality of the corresponding component.

## Mocking

The tests use mocking to isolate the components being tested from their dependencies. This allows testing the components without requiring actual connections to external services like Vault or Redis.