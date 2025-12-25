# Database Migrations (`migrations/`)

This directory contains the database migration scripts managed by **Alembic**.

## Contents

- **`env.py`**: The Alembic environment configuration, which connects to the SQLAlchemy models to generate migrations.
- **`versions/`**: Contains individual Python scripts representing each database schema change.

## Usage

Migrations are automatically applied on application startup in Docker, but can be run manually via:
```bash
alembic upgrade head
```
