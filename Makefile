# Makefile for LatentLens convenience tasks

.PHONY: setup run-local run-docker build push test clean

setup:
	python -m venv venv
	@echo "Activate the venv and install dependencies:"
	@echo "  Windows: .\venv\Scripts\Activate.ps1"
	@echo "  Unix: source venv/bin/activate"
	@echo "Then run: pip install -r requirements.txt"

run-local:
	@echo "Run the API locally (requires venv activation)"
	uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

build:
	docker build -t gatoco/latentlens:latest .

run-docker:
	@echo "Pull image if not present and run container on port 8000"
	docker pull gatoco/latentlens:latest || true
	docker run --rm -p 8000:8000 --name latentlens gatoco/latentlens:latest

push:
	@echo "Tagging and pushing image to Docker Hub (ensure DOCKER_USERNAME/DOCKER_PASSWORD set in env or GitHub Secrets)"
	docker tag gatoco/latentlens:latest gatoco/latentlens:v1.0.0
	docker push gatoco/latentlens:latest
	docker push gatoco/latentlens:v1.0.0

test:
	python scripts/test_docker_deployment.py

clean:
	-docker rm -f latentlens
	@echo "Cleaned up local containers (if existed)"
