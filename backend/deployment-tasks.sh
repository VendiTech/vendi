#!/bin/bash

set -euo pipefail

initialize_application() {
  # Collect static files
  python manage.py collectstatic --noinput

  # Apply database migrations
  python manage.py migrate

  create_superuser
}


# Function to create superuser non-interactively
create_superuser() {
  if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    python manage.py createsuperuser --no-input || true
  else
    echo "Superuser credentials are not set. Skipping superuser creation."
  fi
}

initialize_application

echo "$DJANGO_PORT"
exec python manage.py runserver 0.0.0.0:8080
