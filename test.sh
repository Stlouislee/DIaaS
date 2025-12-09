#!/bin/bash
# Simple test runner that sets PYTHONPATH

export PYTHONPATH=/workspaces/DIaaS

if [ "$1" = "unit" ]; then
    echo "Running unit tests..."
    pytest tests/unit -v
elif [ "$1" = "integration" ]; then
    echo "Running integration tests..."
    pytest tests/integration -v
elif [ "$1" = "e2e" ]; then
    echo "Running E2E tests..."
    pytest tests/e2e -v -s
elif [ "$1" = "coverage" ]; then
    echo "Running tests with coverage..."
    pytest tests/unit tests/integration --cov=app --cov-report=html --cov-report=term-missing
else
    echo "Running all tests..."
    pytest tests -v
fi
