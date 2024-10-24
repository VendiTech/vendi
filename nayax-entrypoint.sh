#!/bin/sh

echo "Starting Nayax consumer..."

# Start Nayax consumer
exec python -m mspy_vendi.consumers.nayax_consumer
