#!/bin/bash
# Script to start the Celery worker for the shaboom project

# If you use a virtual environment, uncomment the line below and set the correct path
# echo "Activating virtual environment..."
# source .venv/bin/activate # Or your virtualenv path e.g., env/bin/activate

echo "Starting Celery worker for shaboom (logs will appear below)..."
celery -A shaboom.celery worker --loglevel=info
