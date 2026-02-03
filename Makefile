.PHONY: install install-dev test test-cov lint format clean run serve docker-build docker-run help

# Default target
help:
	@echo "MermaidView - Available commands:"
	@echo ""
	@echo "  install       Install production dependencies"
	@echo "  install-dev   Install development dependencies"
	@echo "  playwright    Install Playwright browsers"
	@echo "  test          Run tests"
	@echo "  test-cov      Run tests with coverage"
	@echo "  lint          Run linters"
	@echo "  format        Format code"
	@echo "  clean         Clean build artifacts"
	@echo "  run           Run CLI example"
	@echo "  serve         Start web server"
	@echo "  docker-build  Build Docker image"
	@echo "  docker-run    Run Docker container"
	@echo ""

# Installation
install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

playwright:
	playwright install chromium

# Testing
test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=src/mermaid_view --cov-report=html --cov-report=term

# Code quality
lint:
	ruff check src/ tests/
	mypy src/

format:
	black src/ tests/
	isort src/ tests/

# Cleaning
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Running
run:
	mermaid-view render --code "graph TD; A-->B; B-->C" -o output.png

serve:
	mermaid-view serve --port 8000

# Docker
docker-build:
	docker build -t mermaid-view -f docker/Dockerfile .

docker-run:
	docker run -p 8000:8000 -v $(PWD)/output:/app/output mermaid-view

docker-compose-up:
	docker-compose up --build

docker-compose-down:
	docker-compose down
