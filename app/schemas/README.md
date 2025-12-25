# Data Schemas (`app/schemas/`)

This directory contains Pydantic models used for data validation, serialization, and API contracts.

## Files

- **`data.py`**:
    - `UnifiedDataRead`: Schema for data returned by the API.
    - `UnifiedDataCreate`: Internal schema used for transformation.
    - `HealthStatus`: Schema for the system health check response.
    - `ETLStats`: Schema for the ETL performance statistics response.

## Usage

These schemas ensure that all data moving between the API, the database, and the frontend is validated and follows a consistent structure.
