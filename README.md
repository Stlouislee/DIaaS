# Data Infrastructure Service

A comprehensive Data Infrastructure as a Service that allows users to manage **Tabular** (PostgreSQL) and **Graph** (Neo4j) datasets within isolated **Sessions**.

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Testing](#testing)
- [Usage Guide](#usage-guide)
- [Configuration](#configuration)
- [Documentation](#documentation)

## Features

- **Hybrid Storage**: Seamlessly manage structured tabular data and complex graph relationships.
- **Session Isolation**: All data is scoped to specific user sessions for organization and security.
- **Rich API**:
    - **Tabular**: Dynamic table creation, schema management, and SQL-like querying.
    - **Graph**: Node/Edge management and graph algorithms (e.g., Shortest Path).
    - **Export**: Download full sessions or individual datasets as ZIP/CSV/JSON.
    - **Filtering**: URL-based filters (e.g., `?age=gt:30`).
- **Authentication**: Secure API configuration using `X-API-Key`.

## Tech Stack

- **Backend**: Python (FastAPI), Uvicorn
- **Database**: PostgreSQL (Tabular), Neo4j (Graph)
- **Infrastructure**: Docker, Docker Compose

## Getting Started

### Prerequisites

- Docker
- Docker Compose
- Python 3.11+ (for local development)

### Running the Service

1.  **Clone the repository** (if applicable).
2.  **Start the services**:

    ```bash
    sudo docker compose up --build -d
    ```

3.  **Verify Status**:
    The API will be available at `http://localhost:8000`.
    -   API Documentation (Swagger UI): `http://localhost:8000/docs`
    -   Health Check: `http://localhost:8000/health`

### Running Tests

The project includes comprehensive test coverage with unit, integration, and end-to-end tests.

```bash
# Run all unit tests (fast)
./test.sh unit

# Run integration tests
./test.sh integration

# Run end-to-end tests (starts Docker automatically)
./test.sh e2e

# Run all tests
./test.sh all

# Generate coverage report
./test.sh coverage
```

For detailed testing documentation, see [Testing Guide](README_TESTING.md).

### Port Configuration

To avoid conflicts with local services, the `docker-compose.yml` maps ports as follows:

| Service  | Internal Port | Host Port |
| :--- | :--- | :--- |
| **API**      | 8000 | 8000 |
| **Postgres** | 5432 | 5433 |
| **Neo4j**    | 7474 | 7475 |
| **Neo4j**    | 7687 | 7688 |

## Usage Guide

All API requests (except registration) require the `X-API-Key` header.

### 1. Authentication
Register to get a new API Key.

```bash
curl -X POST http://localhost:8000/api/v1/users/register
# Response: {"user_id": "...", "api_key": "YOUR_KEY_HERE", ...}
```

Save your key:
```bash
export API_KEY="YOUR_KEY_HERE"
```

### 2. Session Management
Create a workspace for your data.

```bash
curl -H "X-API-Key: $API_KEY" -X POST http://localhost:8000/api/v1/sessions/ \
  -d '{"name": "Analysis 2024", "description": "Q1 Data"}' \
  -H "Content-Type: application/json"
```

### 3. Tabular Data
Create a table and insert data.

**Create Dataset:**
```bash
curl -H "X-API-Key: $API_KEY" -X POST http://localhost:8000/api/v1/sessions/{session_id}/datasets/tabular \
  -d '{"name": "users", "schema_def": {"name": "VARCHAR", "age": "INTEGER"}}' \
  -H "Content-Type: application/json"
```

**Insert Records:**
```bash
curl -H "X-API-Key: $API_KEY" -X POST http://localhost:8000/api/v1/sessions/{session_id}/datasets/tabular/{dataset_id}/records \
  -d '{"rows": [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]}' \
  -H "Content-Type: application/json"
```

### 4. Graph Data
Manage nodes and relationships.

**Create Graph Dataset:**
```bash
curl -H "X-API-Key: $API_KEY" -X POST http://localhost:8000/api/v1/sessions/{session_id}/datasets/graph \
  -d '{"name": "social_network"}' \
  -H "Content-Type: application/json"
```

**Add Node:**
```bash
curl -H "X-API-Key: $API_KEY" -X POST http://localhost:8000/api/v1/sessions/{session_id}/datasets/graph/{dataset_id}/nodes \
  -d '{"label": "Person", "properties": {"name": "Alice"}}' \
  -H "Content-Type: application/json"
```

### 5. Export
Download all your data as a ZIP file.

```bash
curl -H "X-API-Key: $API_KEY" -O -J http://localhost:8000/api/v1/sessions/{session_id}/export
```

## Testing

This project includes a comprehensive test suite with **59 tests** covering unit, integration, and end-to-end scenarios.

### Quick Start

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run all tests
./run_tests.sh all

# Run with coverage
./run_tests.sh coverage
```

### Test Categories

- **Unit Tests** (24 tests): Core logic, dependencies, security
- **Integration Tests** (31 tests): API endpoints, database interactions
- **E2E Tests** (4 tests): Complete workflows

### Useful Commands

```bash
./run_tests.sh unit           # Fast unit tests only
./run_tests.sh integration    # API integration tests
./run_tests.sh e2e            # End-to-end workflows
pytest -v -k "session"        # Run tests matching keyword
```

📚 **Documentation**:
- [Quick Start Guide](TESTS_QUICKSTART.md) - Get started with testing
- [Complete Testing Guide](TESTING.md) - Detailed documentation
- [Test Summary](TEST_SUMMARY.md) - Full test coverage details

## Configuration

Environment variables can be set in `docker-compose.yml` or a `.env` file.

- `ALLOWED_KEYS`: JSON list of valid API keys (e.g., `["secret-key-1"]`). If empty (default), any key matching the format is accepted.
- `POSTGRES_...`: Database credentials.
- `NEO4J_...`: Graph database credentials.

## Architecture

### Dependency Injection Pattern

The project uses FastAPI's dependency injection system for authorization and validation. All API endpoints leverage reusable dependency functions for:

- Session ownership verification
- Dataset access control
- User authentication

This approach provides:
- **Code reusability**: Validation logic defined once, used everywhere
- **Type safety**: Full IDE support and type checking
- **Maintainability**: Single source of truth for authorization logic
- **Testability**: Easy to mock dependencies in tests

For details, see [Dependency Injection Pattern](docs/DEPENDENCY_INJECTION_PATTERN.md).

## Testing

The project includes a comprehensive three-tier testing strategy:

- **Unit Tests** (27 tests): Fast, isolated component tests
- **Integration Tests** (30+ tests): API endpoint testing with in-memory database
- **End-to-End Tests** (15+ tests): Full workflow testing with Docker environment

**Total: 72+ test cases**

### Quick Test Commands

```bash
# Unit tests only (fastest ~0.3s)
./test.sh unit

# Integration tests (~0.8s)
./test.sh integration

# E2E tests with Docker (~90s)
./test.sh e2e

# All tests
./test.sh all

# With coverage report
./test.sh coverage
```

See [Testing Guide](README_TESTING.md) for comprehensive documentation.

## CI/CD

The project uses GitHub Actions for continuous integration:
- Runs unit tests on every push/PR
- Runs E2E tests with full Docker environment
- Configuration: `.github/workflows/test.yml`

## Documentation

### 📖 API & Usage
- [README](README.md) - Main documentation
- [Implementation Plan](implementation_plan.md) - Project architecture

### 🧪 Testing
- [Tests Quick Start](TESTS_QUICKSTART.md) - Get started with testing
- [Testing Guide](TESTING.md) - Complete testing documentation
- [Test Summary](TEST_SUMMARY.md) - Test coverage details

### 🏗️ Architecture & Refactoring
- [Dependency Injection Pattern](docs/DEPENDENCY_INJECTION_PATTERN.md) - Design pattern explained
- [Before/After Comparison](docs/BEFORE_AFTER_COMPARISON.md) - Code improvements
- [Refactoring Summary](REFACTORING_SUMMARY.md) - Recent improvements

## Contributing

Contributions are welcome! Please ensure:
1. All tests pass (`./run_tests.sh all`)
2. New features include tests
3. Code follows existing patterns
4. Coverage doesn't decrease

## License

[Your License Here]
