# Application Root (`app/`)

The `app/` directory is the core of the Kasparro system, housing all business logic, API definitions, and data processing engines. It is structured as a modular Python package to ensure scalability and maintainability.

## Architecture & Modular Design

The application follows a layered architecture:

1.  **Entry Layer (`main.py`)**: Boots the system and configures global settings.
2.  **API Layer (`api/`)**: External interface for consumers.
3.  **Domain Layer (`core/`, `schemas/`)**: Business models and data contracts.
4.  **Infrastructure Layer (`ingestion/`)**: External data source integration.

## Key Components

- **`main.py`**: The central nervous system of the FastAPI application.

  - **Initialization**: Sets up the FastAPI instance with project metadata.
  - **Middlewares**: Implements CORS, custom latency headers (`X-API-Latency-MS`), and Prometheus instrumentation.
  - **Static Mounting**: Serves the frontend dashboard from `app/static/`.
  - **Router Inclusion**: Aggregates all endpoint modules into the main application.

- **`api/`**: Contains the RESTful controllers. Each module here corresponds to a specific domain (e.g., data retrieval, health monitoring).

- **`core/`**: The backbone of the application, managing database connections via SQLAlchemy and application settings via Pydantic.

- **`ingestion/`**: The ETL (Extract, Transform, Load) engine. It is designed to be extensible, allowing new data sources (like new APIs or file formats) to be added by simply implementing the `BaseExtractor` interface.

- **`schemas/`**: Provides strict type safety and validation using Pydantic. This ensures that data is verified at the system boundaries (API inputs and outputs).

- **`static/`**: A lightweight frontend implementation using Alpine.js and Tailwind CSS, providing a real-time view of the system's performance and data.

- **`tests/`**: A comprehensive test suite using `pytest` and `httpx`, covering both unit logic and end-to-end API flows.

## Development Workflow

When adding a new feature:

1.  Define the database model in `core/models.py`.
2.  Create a Pydantic schema in `schemas/data.py`.
3.  Implement the logic in `api/endpoints.py` or a new ingestion source in `ingestion/`.
4.  Add tests in `tests/` to verify the implementation.
