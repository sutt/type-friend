#!/bin/bash

set -e
set -a

API_IMAGE_NAME="type-friend:latest"
API_CONTAINER_NAME="type-friend-container"
API_MAPPED_PORT=8000

if [ -f .env ]; then
  . ./.env
else
    echo "WARNING: could not find .env file. Running with all default args"
fi

docker build -t "$API_IMAGE_NAME" .
docker stop "$API_CONTAINER_NAME" && docker rm "$API_CONTAINER_NAME" || true
docker run -d --name "$API_CONTAINER_NAME" -p "$API_MAPPED_PORT":8000 "$API_IMAGE_NAME"
echo "Deploy complete. Container '$API_CONTAINER_NAME' running on port: $API_MAPPED_PORT"

