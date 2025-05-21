#!/bin/bash

# Exit on any error
set -e

# Database name (should match your test settings)
DB_NAME="test_shaboom"

# Drop the test database if it exists
echo "Dropping test database if it exists..."
dropdb --if-exists -U postgres "$DB_NAME"

# Create a fresh test database
echo "Creating test database..."
createdb -U postgres "$DB_NAME"

# Set up the database schema using migrations
echo "Running migrations..."
python manage.py migrate --database=default

# If you have any fixtures to load, uncomment the following line
# python manage.py loaddata your_fixture.json --database=default

echo "Test database setup complete!"
