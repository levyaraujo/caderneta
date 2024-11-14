#!/bin/bash

# Function to check if Postgres is ready
wait_for_postgres() {
    echo "Waiting for PostgreSQL to become available..."
    while ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; do
        echo "PostgreSQL is unavailable - sleeping"
        sleep 1
    done
    echo "PostgreSQL is up and running!"
}

# Wait for PostgreSQL
wait_for_postgres

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Start the application
echo "Starting the application..."
exec "$@"
