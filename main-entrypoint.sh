#!/bin/sh

initialize_application() {
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

echo "Applying initial set up"

initialize_application

# Run any other commands you want here
echo "Starting Gunicorn..."

# Start Gunicorn
exec gunicorn mspy_vendi.app.wsgi:application --bind 0.0.0.0:$PORT
