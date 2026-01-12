#!/bin/bash
# Startup script for Render deployment
# Runs migrations and imports data if needed

set -e

echo "Starting Nayi Umeed deployment..."

# Run migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Check if data import is needed
if [ -f "local_data_export.json" ]; then
    echo "Data export file found. Importing data..."
    python import_to_render.py local_data_export.json <<< "yes"
    echo "Data import completed!"
    
    # Clean up after import
    rm -f local_data_export.json
    echo "Data file cleaned up."
else
    echo "No data export file found. Skipping import."
fi

# Start the application
echo "Starting Gunicorn server..."
exec gunicorn nayi_umeed.wsgi:application
