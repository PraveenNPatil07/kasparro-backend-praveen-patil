# Core Infrastructure (`app/core/`)

The `core/` directory contains the foundational infrastructure required to run the application, including configuration management, database persistence, and system-wide utilities.

## Database Implementation (PostgreSQL)

The system uses **PostgreSQL 15** as its primary data store. The implementation details are as follows:

### 1. Connection Management (`database.py`)
- **SQLAlchemy 2.0**: Uses the latest ORM features for efficient querying.
- **Engine Pooling**: Configured with connection pooling to handle concurrent API requests without exhausting database resources.
- **Session Lifecycle**: Implements a "Session-per-request" pattern via FastAPI dependencies, ensuring every transaction is properly closed or rolled back on error.

### 2. Schema Design (`models.py`)
- **`UnifiedData`**: Uses a generalized schema to store data from diverse sources (API, RSS, CSV). Key fields include `title`, `description`, `content_hash` (for deduplication), and `source`.
- **`ETLRun`**: Tracks every execution of the ETL pipeline. It stores metadata like `start_time`, `end_time`, `status`, and `error_message`.
- **`ETLCheckpoint`**: A critical table for **Incremental Ingestion**. It stores the `last_ingested_at` timestamp for each data source, ensuring we only fetch new data in subsequent runs.

### 3. Migrations (Alembic)
- Database changes are never applied manually. We use **Alembic** to version-control the schema.
- Migrations are stored in the root `migrations/` directory and applied automatically during the Docker container startup.

## Configuration Management (`config.py`)

- **Pydantic Settings**: Centralizes all environment variables (DB URLs, API Keys, Log Levels).
- **Environment Awareness**: Supports `.env` files for local development and environment variables for production (Docker/Kubernetes).
- **Validation**: Automatically validates that required configuration (like `DATABASE_URL`) is present before the app starts.

## Utilities

- **`rate_limiter.py`**: A thread-safe, in-memory implementation of a Fixed Window rate limiter. It protects the API from excessive traffic by tracking IP addresses and request counts.
