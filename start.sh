#!/bin/bash

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Run initial ETL ingestion in background
echo "Starting initial ETL ingestion..."
python -m app.ingestion.runner &

# Start the application
echo "Starting application..."
PORT=${PORT:-8000}
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 4
