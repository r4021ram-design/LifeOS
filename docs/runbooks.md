# LifeOS AI – Operations & Incident Runbooks

This document provides step-by-step procedures for mitigating common production incidents.

---

## Runbook 1: High CPU / Memory Spikes on Backend App

### Symptom
FastAPI container reaches 95%+ CPU or memory capacity, resulting in latency increases and 504 timeouts.

### Diagnostics
1. Check process usage inside the container:
   ```bash
   docker exec -it <container_id> top
   ```
2. Inspect slow API queries in Grafana Tempo / OpenTelemetry logs.

### Remediation
1. **Vertical / Horizontal Scale:** If due to traffic surge, scale the container replicas:
   ```bash
   docker-compose up --scale backend=4 -d
   ```
2. **Rate Limiting:** If due to API abuse, inspect source IP in reverse proxy logs and add rate limit blocks in Nginx or Cloudflare.

---

## Runbook 2: Database Connection Pool Exhaustion

### Symptom
FastAPI logs show:
```text
sqlalchemy.exc.TimeoutError: QueuePool limit of size 5 overflow 10 reached, connection timed out
```

### Diagnostics
1. View active connections on Postgres:
   ```sql
   SELECT COUNT(*), state FROM pg_stat_activity GROUP BY state;
   ```
2. Verify if connection leak exists (unclosed DB sessions in code).

### Remediation
1. **Reboot Connections:** Restarting FastAPI forces SQLAlchemy pool cleanup:
   ```bash
   docker-compose restart backend
   ```
2. **Tuning Settings:** Modify pool sizes in config variables:
   * Increase `SQLALCHEMY_POOL_SIZE` (default 5 to 20).
   * Increase `SQLALCHEMY_MAX_OVERFLOW` (default 10 to 30).
3. **Verify closing:** Review recent commits to ensure all queries wrap inside a context manager or use FastAPI's `Depends(get_db)`.

---

## Runbook 3: Celery Worker backlog

### Symptom
Reminders or tasks do not fire on schedule. Celery broker (Redis) queue size is growing.

### Diagnostics
1. Inspect celery queue size:
   ```bash
   redis-cli -u redis://redis:6379/0 LLEN celery
   ```
2. Ping worker status:
   ```bash
   celery -A app.core.celery_app inspect ping
   ```

### Remediation
1. **Add Worker Concurrency:** Start additional workers:
   ```bash
   docker-compose up --scale worker=3 -d
   ```
2. **Purge Non-Critical Tasks:** If queue has stale reminders, purge the queue (Warning: deletes pending items):
   ```bash
   celery -A app.core.celery_app purge
   ```
