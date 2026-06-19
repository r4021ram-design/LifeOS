# LifeOS AI – Launch Readiness Checklist

This checklist tracks tasks required to successfully launch LifeOS AI into production environments.

---

## 1. Domain, DNS, & Security Headers
- [ ] **DNS Mapping:** Map `api.lifeos-ai.com` and `lifeos-ai.com` to target reverse proxies.
- [ ] **SSL Certificates:** Verify Let's Encrypt certificates automatically renew.
- [ ] **Security Headers:** Verify the backend returns standard headers:
  - `X-Frame-Options: DENY`
  - `X-Content-Type-Options: nosniff`
  - `X-XSS-Protection: 1; mode=block`
  - `Strict-Transport-Security`

## 2. Secrets & Environment Settings
- [ ] **SECRET_KEY Rotation:** Change backend settings `SECRET_KEY` from default dev keys to a secure, cryptographically random key.
- [ ] **Sentry Activation:** Verify `SENTRY_DSN` is populated and configured with staging/production profiles.
- [ ] **API Keys Validation:** Ensure OpenAI, Gemini, Kotak Neo, and FYERS keys are securely managed via AWS Secrets Manager or GCP Secret Manager.
- [ ] **Database Connection Strings:** Assert production environment utilizes TLS connections to PostgreSQL:
  ```text
  DATABASE_URL=postgresql+psycopg2://user:passwd@pg-host:5432/dbname?sslmode=require
  ```

## 3. Database & Migrations
- [ ] **Schema Check:** Run Alembic migration validation:
  - `alembic upgrade head` completes cleanly on production postgres engine.
- [ ] **GIN Indexes:** Validate database creates the GIN full-text search indexes on the production Postgres engine.

## 4. Notifications & Workers
- [ ] **Celery Queues:** Verify worker containers are running and actively listening on tasks queue.
- [ ] **Exponential Backoff & DLQ:** Validate Celery correctly retries failed notifications and marks dead messages as `Failed` in DB.
- [ ] **Scheduler Daemon:** Verify APScheduler background thread initiates on startup.

## 5. Monitoring & Observability
- [ ] **Prometheus:** Confirm scraper reads `/metrics` endpoint and records counts.
- [ ] **Grafana Dashboard:** Import `lifeos_dashboard.json` and verify panels display metrics without errors.
- [ ] **OpenTelemetry Trace Export:** Verify application traces populate to OpenTelemetry Collector or Tempo agent.
