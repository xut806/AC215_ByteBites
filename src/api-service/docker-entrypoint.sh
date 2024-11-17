#!/bin/bash

echo "Starting the container..."

# Run the API server
uvicorn api.service:app --host 0.0.0.0 --port 9000
