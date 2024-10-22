#!/bin/bash

set -euo pipefail

# Initialize the variable
ACTION=""

# Check if the number of command line arguments passed to the script is greater than or equal to 1.
if [ $# -ge 1 ]; then
  # Assign the value of the first command line argument (${1}) to the variable ACTION
  ACTION=${1};
  # Shift the positional parameters to the left, discarding the first argument.
  shift;
fi

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

case "${ACTION}" in

  ''|-*) # Default for Local server up
    initialize_application

    exec python manage.py runserver 0.0.0.0:"$DJANGO_PORT"
    ;;

  run_gunicorn) # Default for Production server up
    initialize_application

    exec gunicorn app.wsgi:application --bind 0.0.0.0:"$DJANGO_PORT"
    ;;

  *) # For script running
    exec ${ACTION} ${@}
    ;;
esac
