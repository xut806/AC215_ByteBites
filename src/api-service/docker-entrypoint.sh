#!/bin/bash

echo "Starting the container..."

uvicorn_server() {
    uvicorn api.service:app --host 0.0.0.0 --port 9000 --log-level debug --reload --reload-dir api/ "$@"
}

uvicorn_server_production() {
    pipenv run uvicorn api.service:app --host 0.0.0.0 --port 9000 --lifespan on
}

export -f uvicorn_server
export -f uvicorn_server_production

if [ "${DEV}" = "1" ]; then
  echo "Running in development mode..."
  uvicorn_server
else
  echo "Running in production mode..."
  uvicorn_server_production
fi
