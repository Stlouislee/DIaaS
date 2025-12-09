.PHONY: help install test test-unit test-integration test-e2e test-all coverage docker-up docker-down clean

help:
	@echo "Available commands:"
	@echo "  make install          - Install dependencies"
	@echo "  make test-unit        - Run unit tests only"
	@echo "  make test-integration - Run integration tests only"
	@echo "  make test-e2e         - Run end-to-end tests (starts Docker)"
	@echo "  make test-all         - Run all tests"
	@echo "  make coverage         - Run tests with coverage report"
	@echo "  make docker-up        - Start Docker services"
	@echo "  make docker-down      - Stop Docker services"
	@echo "  make clean            - Clean up test artifacts"

install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

test-unit:
	@echo "Running unit tests..."
	pytest tests/unit -v -m "not e2e and not integration"

test-integration:
	@echo "Running integration tests..."
	pytest tests/integration -v -m "integration"

test-e2e:
	@echo "Running end-to-end tests (this will start Docker)..."
	pytest tests/e2e -v -m "e2e" -s

test-all:
	@echo "Running all tests..."
	pytest tests -v

coverage:
	@echo "Running tests with coverage..."
	pytest tests --cov=app --cov-report=html --cov-report=term-missing

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down -v

clean:
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
