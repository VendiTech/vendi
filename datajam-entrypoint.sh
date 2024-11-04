#!/bin/sh

echo "Starting Datajam consumer..."

# Start scheduler
taskiq scheduler mspy_vendi.consumers.datajam_consumer:scheduler &

# Start Datajam consumer
exec taskiq worker mspy_vendi.consumers.datajam_consumer:broker -w 1 --ack-type when_executed --no-configure-logging
