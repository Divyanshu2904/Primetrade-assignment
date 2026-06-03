#!/bin/sh

set -e

echo "Waiting for PostgreSQL database..."

python -c "
import socket
import time
import os
from urllib.parse import urlparse

db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:password@db:5432/taskmaster_db')
url = urlparse(db_url)
host = url.hostname
port = url.port or 5432

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
while True:
    try:
        s.connect((host, port))
        s.close()
        break
    except socket.error:
        time.sleep(1)
"

echo "PostgreSQL is ready!"

# Initialize migrations directory if it doesn't exist
if [ ! -d "migrations" ]; then
    echo "Initializing Flask migrations..."
    flask db init
fi

# Generate initial migration if no version exists
if [ ! -d "migrations/versions" ] || [ -z "$(ls -A migrations/versions 2>/dev/null)" ]; then
    echo "Creating initial database migration..."
    flask db migrate -m "Initial migration"
fi

echo "Applying database migrations..."
flask db upgrade

echo "Ensuring admin user exists..."
flask create-admin

echo "Starting Flask Server..."
exec python run.py
