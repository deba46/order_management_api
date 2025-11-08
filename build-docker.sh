#!/bin/bash

# Build and test Docker image locally

set -e

IMAGE_NAME="order-management-api"
IMAGE_TAG="latest"

echo "🔨 Building Docker image..."
docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .

echo ""
echo "📊 Image size:"
docker images ${IMAGE_NAME}:${IMAGE_TAG} --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

echo ""
echo "🔍 Verifying non-root user..."
docker run --rm ${IMAGE_NAME}:${IMAGE_TAG} whoami

echo ""
echo "🧪 Testing container locally..."
echo "Starting container on port 8000..."

# Run container in background
CONTAINER_ID=$(docker run -d \
  -p 8000:8000 \
  -e POSTGRES_HOST=host.docker.internal \
  -e POSTGRES_PORT=5433 \
  -e POSTGRES_USER=orders \
  -e POSTGRES_PASSWORD=PrefectPassword123 \
  -e POSTGRES_DB=server \
  ${IMAGE_NAME}:${IMAGE_TAG})

echo "Container started: $CONTAINER_ID"
echo ""
echo "⏳ Waiting for application to start..."
sleep 5

echo ""
echo "🏥 Health check:"
curl -f http://localhost:8000/health || echo "Health check failed"

echo ""
echo ""
echo "✅ Container is running!"
echo ""
echo "Test the API:"
echo "  curl http://localhost:8000/health"
echo "  curl http://localhost:8000/orders"
echo "  curl -X POST http://localhost:8000/orders -H 'Content-Type: application/json' -d '{\"amount\": 99.99}'"
echo ""
echo "View logs:"
echo "  docker logs -f $CONTAINER_ID"
echo ""
echo "Stop container:"
echo "  docker stop $CONTAINER_ID"
