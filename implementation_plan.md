# Data Infrastructure as a Service - Implementation Plan

## Goal Description
Build a RESTful API service that allows users to create "Sessions" containing multiple datasets.
Supported data types:
1.  **Tabular**: Stored in PostgreSQL.
2.  **Graph**: Stored in Neo4j.

## User Review Required
> [!IMPORTANT]
> **Delivery**: The application will be delivered as a Docker container, orchestrating with Postgres and Neo4j via `docker-compose`.
> **API Design**: To support "most operations", I will expose:
> 1.  **Schema Operations**: Endpoints to manipulate tables/nodes definitions.
> 2.  **Data Operations**: CRUD for individual records.
> 3.  **Query Operations**: A flexible `POST /query` endpoint allowing raw (or safely parameterized) SQL/Cypher execution for maximum power, alongside structured endpoints for common actions.
> 4.  **Security**: Access controlled via `X-API-Key`.
>     - **Config**: `ALLOWED_KEYS` environment variable.
>     - **Behavior**: If `ALLOWED_KEYS` is set, usage requires a listed key. If empty, any key (matching format) is accepted.
>     - **Purpose**: Key serves as the **User ID** for data isolation in both modes.

## Proposed Changes


### Project Structure
Root: `/home/debian/.gemini/antigravity/scratch/data-infra-service`

#### [NEW] Dependencies
- `requirements.txt` or `pyproject.toml`
    - `fastapi`, `uvicorn` (Server)
    - `sqlalchemy`, `asyncpg` (Postgres ORM/Driver)
    - `neo4j` (Neo4j Driver)
    - `pydantic` (Validation)
    - `passlib`, `bcrypt` (if hashing needed, though API keys are usually random strings)
    - `python-multipart` (for potential API key header handling)

### Core Components

#### [NEW] Containerization
- `Dockerfile`: Multi-stage build for the Python application.
- `docker-compose.yml`: Services for `api`, `postgres`, `neo4j`.

#### [NEW] Authentication Service
- **Config**: `ALLOWED_KEYS` (list of strings).
- **Middleware**:
    1. Extract `X-API-Key` header.
    2. **Format Validation**: Ensure key matches regex (e.g., `^[a-zA-Z0-9_\-]{8,64}$`).
    3. **Permission Check**: If `ALLOWED_KEYS` is not empty, check strict inclusion.
    4. **Context**: Set `current_user_id = api_key`.
- **Note**: No DB table needed for users if we just use the key as the ID directly. We will treat the "User" as ephemeral based on the key provided.

#### [NEW] Session Manager
- Logic to create/retrieve sessions.
- **Isolation**: All queries filtered by `user_id`. Each session belongs to a user.
- Each session acts as a namespace (e.g., separate Postgres Schemas, Neo4j Database labels/prefixes).

#### [NEW] Data Services
- **TabularService**:
    - Manage Table Schemas (DDL).
    - Data Manipulation (DML).
    - Advanced Querying (Aggregations, Joins via SQL).
- **GraphService**:
    - Manage Node Labels / Relationship Types.
    - Path finding and standard graph algos.
    - Cypher Query execution.
- **ExportService**:
    - **Tabular**: Export to CSV, JSON.
    - **Graph**: Export to JSON (Node-Link), GraphML.
    - **Session**: Bundle all dataset exports into a ZIP file.

### API Layer
- **Auth**:
    - `POST /users`: Register user (Receive API Key).
    - `POST /users/key`: Rotate/Create new API Key.
- **Sessions** (All require `X-API-Key`):
    - `POST /sessions`: Create session (Scoped to User).
    - `GET /sessions`: List User's sessions.
- **Datasets (Schema)**:
    - `POST /sessions/{id}/datasets`: Register/Create a dataset.
    - `GET /sessions/{id}/datasets`: List datasets.
    - `PUT /sessions/{id}/datasets/{dataset_id}`: Update schema.
    - `DELETE /sessions/{id}/datasets/{dataset_id}`: Drop dataset/table.
- **Data (Records)**:
    - `POST /sessions/{id}/datasets/{dataset_id}/records`: Insert/Upsert data (Bulk support).
    - `GET /sessions/{id}/datasets/{dataset_id}/records`: List records.
        - **Rich Features**:
            - **Filtering**: `?name=eq:Alice&age=gt:30`
            - **Selection**: `?select=id,name,email`
            - **Sorting**: `?sort=created_at:desc`
            - **Pagination**: `?limit=50&offset=0`
    - `PUT /sessions/{id}/datasets/{dataset_id}/records`: Update records (Bulk or Filter-based).
    - `DELETE /sessions/{id}/datasets/{dataset_id}/records`: Delete records (Filter-based).

- **Graph Specific**:
    - `GET /sessions/{id}/datasets/{dataset_id}/nodes`: Search nodes by label/property.
    - `GET /sessions/{id}/datasets/{dataset_id}/nodes/{node_id}/neighbors`: Traversal (expand 1 hop).
    - `POST /sessions/{id}/datasets/{dataset_id}/algorithms/shortest_path`: Execute path finding.

- **Advanced Query**:
    - `POST /sessions/{id}/query`: Execute raw/structured query (SQL or Cypher).
    - **Safe Mode**: Parameterized queries only.

- **Export**:
    - `GET /sessions/{id}/export`: Download ZIP of all datasets in session.
    - `GET /sessions/{id}/datasets/{dataset_id}/export`: Download single dataset (Format query param: csv, json, graphml).




## Verification Plan
### Automated Tests
- Pytest for unit tests.
- Testcontainers or mocked drivers for database integration tests.
