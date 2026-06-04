#!/bin/sh
set -e

alembic upgrade head 2>&1 | grep -v "^%(" || true

exec gunicorn src.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
