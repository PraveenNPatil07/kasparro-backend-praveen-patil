# Automated Tests (`app/tests/`)

This directory contains the test suite for the application, built with `pytest`.

## Files

- **`conftest.py`**: Defines shared fixtures, including a mock database session that uses an in-memory SQLite database (or a test PostgreSQL instance) to ensure test isolation.
- **`test_api.py`**: Integration tests for the FastAPI routes, covering data retrieval, health checks, and rate limiting.
- **`test_ingestion.py`**: Unit and integration tests for the ETL pipeline, verifying extraction logic, transformation rules, and incremental checkpointing.

## Running Tests

Execute the following command from the project root:
```bash
pytest
```
or
```bash
make test
```
