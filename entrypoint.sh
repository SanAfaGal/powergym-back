#!/bin/bash
set -e

# Wait for database to be ready
echo "Waiting for database to be ready..."
max_attempts=30
attempt=0

# Debug: Show DATABASE_URL (without password)
echo "Checking DATABASE_URL configuration..."
if [ -z "$DATABASE_URL" ]; then
    echo "ERROR: DATABASE_URL is not set!"
    exit 1
fi
# Show DATABASE_URL with password masked
echo "DATABASE_URL: $(echo $DATABASE_URL | sed 's/:[^:@]*@/:***@/')"

# Check if DATABASE_URL points to postgres service (not localhost)
if echo "$DATABASE_URL" | grep -q "localhost\|127.0.0.1"; then
    echo "WARNING: DATABASE_URL appears to point to localhost!"
    echo "In Docker, you should use 'postgres' as the hostname, not 'localhost'"
    echo "Example: postgresql://user:password@postgres:5432/powergym"
fi

while [ $attempt -lt $max_attempts ]; do
    attempt=$((attempt + 1))
    echo "Attempt $attempt/$max_attempts: Testing database connection..."
    
    # Capture both stdout and stderr to show errors
    # Temporarily disable set -e to capture errors
    set +e
    output=$(uv run python -c "
import sys
import os
try:
    from app.db.session import engine
    from sqlalchemy import text
    with engine.connect() as conn:
        conn.execute(text('SELECT 1'))
    print('SUCCESS: Database connection successful!')
    sys.exit(0)
except Exception as e:
    print(f'ERROR: {type(e).__name__}: {e}', file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)
" 2>&1)
    exit_code=$?
    set -e
    
    if [ $exit_code -eq 0 ]; then
        echo "$output"
        echo "Database is ready!"
        break
    else
        echo "Connection failed. Error details:"
        echo "$output"
        if [ $attempt -lt $max_attempts ]; then
            echo "Waiting 2 seconds before retry..."
            sleep 2
        fi
    fi
done

if [ $attempt -eq $max_attempts ]; then
    echo "ERROR: Database connection failed after $max_attempts attempts"
    echo ""
    echo "Troubleshooting tips:"
    echo "1. Check that DATABASE_URL in .env points to 'postgres:5432' (not localhost)"
    echo "2. Verify postgres service is running: docker-compose ps"
    echo "3. Check postgres logs: docker-compose logs postgres"
    echo "4. Verify network connectivity: docker-compose exec backend ping postgres"
    exit 1
fi

# Run migrations
echo "Running database migrations..."
if ! uv run alembic upgrade head; then
    echo "ERROR: Migration failed"
    exit 1
fi

# Start application
echo "Starting application..."
exec uv run gunicorn main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
