#!/bin/sh
ALEMBIC_PATH=mspy_vendi/db/migrations/alembic.ini

echo "Applying initial set up"

alembic -c ${ALEMBIC_PATH} upgrade head

# Run any other commands you want here
echo "Starting Uvicorn..."

# Start Uvicorn
exec python -m mspy_vendi.server
