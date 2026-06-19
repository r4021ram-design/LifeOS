# Database Schema Creation & Migration Validation Report

This report documents the architectural gating of runtime DDL statements and certifies the migration pattern for production deployment.

## 1. Risk of Automatic Table Creation in Production

In development, calling `Base.metadata.create_all(bind=engine)` automatically creates tables on app startup. In an enterprise production deployment, this creates several severe issues:
1. **Race Conditions:** In containerized environments (e.g., Kubernetes or multi-replica AWS ECS tasks), multiple server replicas launching concurrently will attempt to execute `CREATE TABLE` and `CREATE INDEX` queries on the same target database simultaneously, causing lock contention, database deadlocks, or server startup failures.
2. **Schema Drift:** Schema updates defined in Python models but not written as explicit SQL migrations lead to untracked schema changes that bypass version control, breaking data consistency.
3. **Privilege Overreach:** Application backend roles should ideally have limited DDL privileges in production, leaving administrative tasks like table creation/modification to dedicated migration scripts or CI pipelines.

## 2. Gating Implementation

We have gated the `create_all` database hook inside [main.py](file:///c:/Users/admin/Desktop/todo/backend/app/main.py) to development and testing environments only:

```python
# app/main.py
# Auto-create tables for SQLite / development/testing environments
if settings.ENVIRONMENT in ["development", "testing"]:
    Base.metadata.create_all(bind=engine)
```

In staging and production, the table creation logic is skipped.

## 3. Production Migration Strategy (Alembic)

For staging and production deployments, database schemas must be applied using Alembic. 

1. **Migration Generation (Development):**
   ```bash
   alembic revision --autogenerate -m "description_of_change"
   ```
2. **Reviewing Code:**
   Developers review the generated python migration file under `backend/alembic/versions/` to verify column type definitions, constraints, and index formations.
3. **Applying Migration (Deployment Pipeline):**
   Before launching the backend container replicas, the release orchestration runs:
   ```bash
   alembic upgrade head
   ```
   This ensures that the database schema is updated to the latest revision synchronously, exactly once, before the web servers begin processing traffic.
