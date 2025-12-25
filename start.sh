#!/bin/bash

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Run initial ETL ingestion in background
echo "Starting initial ETL ingestion..."
python -m app.ingestion.runner &

# Start the application
echo "Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
