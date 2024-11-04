#!/bin/bash

set -euo pipefail

# Initialize the variable
ACTION=""
ALEMBIC_PATH=mspy_vendi/db/migrations/alembic.ini

# Check if the number of command line arguments passed to the script is greater than or equal to 1.
if [ $# -ge 1 ]; then
  # Assign the value of the first command line argument (${1}) to the variable ACTION
  ACTION=${1};
  # Shift the positional parameters to the left, discarding the first argument.
  shift;
fi

case "${ACTION}" in

  ''|-*) # Default for Local server up
    alembic -c ${ALEMBIC_PATH} upgrade head

    exec python -m mspy_vendi.server
    ;;

  nayax_consumer)
    exec python -m mspy_vendi.consumers.nayax_consumer
    ;;

  datajam_consumer)
    # Start the scheduler in the background
    taskiq scheduler mspy_vendi.consumers.datajam_consumer:scheduler &

    # Start the worker
    exec taskiq worker mspy_vendi.consumers.datajam_consumer:broker -w 1 --ack-type when_executed --no-configure-logging
    ;;

  *) # For script running
    exec ${ACTION} ${@}
    ;;
esac
