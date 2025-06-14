#!/bin/bash
IMAGE_NAME="type-friend:latest"
CONTAINER_NAME="type-friend-container"

echo "Building image $IMAGE_NAME..."
docker build -t "$IMAGE_NAME" .

echo "Stopping and removing container $CONTAINER_NAME if it exists..."
docker stop "$CONTAINER_NAME" && docker rm "$CONTAINER_NAME" || true

echo "Running new container $CONTAINER_NAME from image $IMAGE_NAME..."
# XXX: Run in detached mode (-d) so the script can complete while the container runs in the background.
# XXX: Adjust port mapping (-p) if your application uses a different port.
docker run -d --name "$CONTAINER_NAME" -p 8000:8000 "$IMAGE_NAME"

echo "Deployment complete. Container $CONTAINER_NAME should be running."
