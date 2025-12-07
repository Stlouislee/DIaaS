# Data Infrastructure Service

A comprehensive Data Infrastructure as a Service that allows users to manage **Tabular** (PostgreSQL) and **Graph** (Neo4j) datasets within isolated **Sessions**.

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

## Configuration

Environment variables can be set in `docker-compose.yml` or a `.env` file.

- `ALLOWED_KEYS`: JSON list of valid API keys (e.g., `["secret-key-1"]`). If empty (default), any key matching the format is accepted.
- `POSTGRES_...`: Database credentials.
- `NEO4J_...`: Graph database credentials.
