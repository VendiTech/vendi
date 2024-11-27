#!/bin/sh

echo "Starting TaskIQ scheduler, consumer..."

# Start the scheduler in the background
taskiq scheduler mspy_vendi.broker:scheduler --skip-first-run &

# Start the worker
exec taskiq worker mspy_vendi.broker:broker -w 1 -fsd --ack-type when_executed --no-configure-logging
