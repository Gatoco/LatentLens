#!/usr/bin/env bash
# Quickstart helper (Unix/macOS)
set -e

echo "1) Pulling Docker image..."
docker pull gatoco/latentlens:latest

echo "2) Running container on http://localhost:8000"
docker run --rm -p 8000:8000 --name latentlens gatoco/latentlens:latest &
CONTAINER_PID=$!

echo "Waiting 10s for initialization..."
sleep 10

echo "Health:"
curl -sS http://localhost:8000/health || true

echo "Open docs at http://localhost:8000/docs"

echo "To stop the container run: docker rm -f latentlens"
