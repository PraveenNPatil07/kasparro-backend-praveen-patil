# Kasparro Backend & ETL System

A production-grade ETL (Extract, Transform, Load) pipeline and Backend API system built with Python, FastAPI, and PostgreSQL.

## 🚀 Architecture Overview

The system is designed with **Clean Architecture** principles, ensuring separation of concerns and maintainability.

- **Ingestion Layer**: Isolated modules for each data source (CSV, API, RSS).
- **Core Layer**: Infrastructure logic including database configuration, logging, and core settings.
- **API Layer**: FastAPI endpoints for data access and system observability.
- **Schema Layer**: Pydantic models for data validation and normalization.
- **Service Layer**: Business logic (transformation rules).

### Data Flow

`Sources → Raw Tables (Immutable) → Validation/Normalization → Unified Tables → API`

## 🛠 Tech Stack

- **Language**: Python 3.11
- **API**: FastAPI (Async, OpenAPI)
- **Database**: PostgreSQL 15
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Validation**: Pydantic v2
- **Observability**: Prometheus
- **Containers**: Docker + Docker Compose

## 🛠 Infrastructure & Implementation

The Kasparro system is built to be modern, resilient, and easily deployable. We rely on **PostgreSQL** for data integrity and **Docker** for consistent environment management.

### 🐘 PostgreSQL Implementation

PostgreSQL serves as the reliable foundation for our data. Our implementation focuses on:

- **Relational Integrity**: We use foreign keys and constraints to ensure that ETL logs, checkpoints, and unified data remain consistent.
- **SQLAlchemy 2.0 ORM**: All database interactions are handled via SQLAlchemy, providing a clean, Pythonic interface while maintaining the ability to write complex, optimized SQL when necessary.
- **Connection Pooling**: To handle high-concurrency API requests, we use connection pooling, which reuses existing database connections rather than creating new ones for every request.
- **Alembic Migrations**: We treat our database schema as code. Every change is tracked in a migration script, allowing us to upgrade or roll back the database state safely across different environments.
- **Data Deduplication**: We implement unique constraints on content hashes, ensuring that even if the same data is ingested multiple times, our database remains clean and free of duplicates.

### 🐳 Docker Implementation

We use Docker and Docker Compose to orchestrate the entire stack into a single, cohesive unit.

- **Containerized Services**:
  - **`db`**: A PostgreSQL 15 container with persistent volume storage for data safety.
  - **`api`**: The FastAPI backend, optimized with multiple Uvicorn workers for production performance.
  - **`etl`**: A dedicated container that runs the ETL ingestion pipeline.
  - **`prometheus`**: A monitoring container that scrapes metrics from the API.
- **Multi-Stage Builds**: Our `Dockerfile` uses multi-stage builds to keep production images small and secure, separating the build environment from the runtime.
- **Service Orchestration**: `docker-compose.yml` manages service dependencies (e.g., ensuring the DB is healthy before the API starts) and internal networking.
- **Health Checks**: Every service includes built-in health checks, allowing Docker to automatically restart containers if they become unresponsive.
- **Environment Isolation**: Docker ensures that "it works on my machine" translates perfectly to "it works in production," isolating dependencies and system configurations.

## 📂 Codebase Structure & Documentation

## ⚡ Quick Start

### Prerequisites

- Docker & Docker Compose
- Make (optional, but recommended)

### Run the system

```bash
# Clone the repository
git clone "https://github.com/PraveenNPatil07/kasparro-backend-praveen-patil.git"
cd kasparro-backend-praveen-patil

# Create .env file
cp .env.example .env

# Start all services
make up
```

The system will automatically:

1. Start PostgreSQL
2. Run database migrations
3. Start the FastAPI service at `http://localhost:8000`
4. Start the ETL runner to ingest data
5. Start Prometheus at `http://localhost:9090`

### Available Commands

- `make up`: Start the system
- `make down`: Stop the system
- `make test`: Run the test suite
- `make logs`: View service logs
- `make etl`: Manually trigger an ETL run

## 📊 API Endpoints

- `GET /api/v1/data`: Paginated and filterable unified records.
- `GET /api/v1/health`: Database and ETL health status.
- `GET /api/v1/stats`: ETL run metadata and performance metrics.
- `GET /api/v1/metrics`: Prometheus metrics (text format).

## 🛡 Design Features

### 1. Incremental Ingestion

The system maintains an `etl_checkpoints` table. Each run only fetches records newer than the last successful checkpoint, preventing redundant processing and saving bandwidth.

### 2. Crash Safety & Idempotency

- **Raw Storage**: Original data is saved in `raw_data` tables before transformation.
- **UPSERT Logic**: Clean data is written using UPSERT (Update or Insert), ensuring no duplicates even if a run is retried.
- **Transaction Safety**: Checkpoints are updated only after successful database commits.

### 3. Observability

- **Prometheus Middleware**: Automatically tracks HTTP request counts and latencies.
- **Custom Headers**: Every API response includes `X-Request-ID` and `X-API-Latency-MS`.
- **Health Checks**: Real-time monitoring of DB connectivity and last ETL success.

## 🧪 Testing Strategy

The system includes:

- **Unit Tests**: For transformation logic.
- **Integration Tests**: For end-to-end ingestion and incremental loading.
- **API Tests**: To verify contracts and pagination.

Run tests via:

```bash
make test
```

## ☁️ Cloud Deployment

This system is designed to be deployed to any major cloud provider (AWS/GCP/Azure) using the provided Docker configuration.

**Recommended Setup:**

- **Database**: Managed RDS (AWS) or Cloud SQL (GCP).
- **API**: AWS App Runner, ECS, or GCP Cloud Run.
- **ETL Runner**: Scheduled Task (AWS EventBridge + ECS RunTask) or Cloud Scheduler + Cloud Run.
- **Monitoring**: CloudWatch or Prometheus/Grafana.
