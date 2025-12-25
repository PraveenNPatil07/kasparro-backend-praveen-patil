# API Layer (`app/api/`)

The API layer acts as the gateway between the backend services and the external world. It is built on **FastAPI**, leveraging its asynchronous capabilities and automatic OpenAPI (Swagger) documentation.

## Endpoint Documentation

### 1. Data Retrieval (`GET /api/v1/data`)
- **Purpose**: Provides a unified view of all ingested data (Crypto, RSS, Products).
- **Features**: 
    - Full-text search on titles and descriptions.
    - Source-based filtering.
    - Pagination for performance.
    - Sorting by creation date (descending).

### 2. System Health (`GET /api/v1/health`)
- **Purpose**: Real-time monitoring for DevOps and administrators.
- **Returns**: 
    - Database connectivity status.
    - Details of the last ETL run (timestamp, duration, success/failure).
    - Success rate calculated from historical runs.

### 3. ETL Orchestration (`POST /api/v1/trigger`)
- **Purpose**: Allows manual intervention to refresh data without waiting for the schedule.
- **Implementation**: Uses FastAPI's `BackgroundTasks` to trigger the `runner.py` script, ensuring the API remains responsive while data is being processed.

### 4. CSV Management (`POST /api/v1/upload-csv`)
- **Purpose**: Enables users to upload custom data files.
- **Workflow**:
    1. Receives a multipart file.
    2. Saves it to a temporary location in `data/`.
    3. Immediately executes the `CSVExtractor` on the new file.
    4. Cleans up temporary files after ingestion.

### 5. Performance Metrics (`GET /api/v1/stats`)
- **Purpose**: Aggregates metadata about ETL runs.
- **Metrics**: Total runs, average success rate, and per-source performance counters.

## Security & Reliability

- **Rate Limiting**: Integrated via a custom middleware to prevent DDoS attacks on high-traffic endpoints.
- **Error Handling**: Standardized JSON error responses for 404 (Not Found), 429 (Too Many Requests), and 500 (Internal Server Error).
- **Dependency Injection**: Every endpoint uses `get_db` to ensure thread-safe database sessions that are automatically closed after the request completes.
