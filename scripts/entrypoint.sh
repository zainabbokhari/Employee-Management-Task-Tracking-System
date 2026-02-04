#!/bin/sh
set -e

echo "Waiting for DB..."
sleep 5

# Run migrations
alembic upgrade head || true

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
