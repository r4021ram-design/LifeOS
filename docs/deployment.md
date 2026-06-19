# LifeOS AI Production Deployment & Monitoring Guide

This document outlines the architecture, configuration, and monitoring strategy for launching LifeOS AI in a production cloud environment.

---

## 1. Production Deployment Architecture

```mermaid
graph TD
    Client[Web Browser / PWA Client] -->|HTTPS| Vercel[Vercel CDN Frontend]
    Client -->|API / WebSockets| Nginx[Nginx Reverse Proxy]
    Nginx -->|Route Request| FastAPI[FastAPI App Server]
    FastAPI -->|Queries| Postgres[(PostgreSQL DB)]
    FastAPI -->|Cache / Queue| Redis[(Redis Broker)]
    Celery[Celery Task Worker] -->|Fetch Jobs| Redis
    Celery -->|Write Result| Postgres
```

---

## 2. Infrastructure Setup & Docker Build

To run the production-ready application containers in a cloud VM:

### Backend Docker Build
1. Build the API container:
   ```bash
   docker build -t lifeos-api:latest ./backend
   ```
2. Run migration tasks and launch server:
   ```bash
   docker run -d --name lifeos-api -p 8000:8000 \
     -e DATABASE_URL="postgresql://user:password@db-host:5432/lifeos" \
     -e REDIS_URL="redis://redis-host:6379/0" \
     lifeos-api:latest
   ```

### Frontend Static Build
1. Run build to create production assets:
   ```bash
   cd frontend && npm run build
   ```
2. Upload the `dist/` folder to Vercel, Netlify, or an S3 bucket with CloudFront.

---

## 3. Nginx Reverse Proxy Configuration

Place the following configuration in `/etc/nginx/sites-available/lifeos`:

```nginx
server {
    listen 80;
    server_name api.lifeos-ai.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
    }
}
```

---

## 4. Monitoring & Observability Setup

### Sentry Integration (Error Tracking)
Initialize Sentry inside `backend/app/main.py`:
```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="YOUR_SENTRY_DSN",
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0,
)
```

### Prometheus & Grafana Metric Scrapes
1. We expose metrics in FastAPI using `prometheus-fastapi-instrumentator`.
2. Configure Prometheus target in `prometheus.yml`:
   ```yaml
   scrape_configs:
     - job_name: 'lifeos-api'
       scrape_interval: 5s
       metrics_path: '/metrics'
       static_configs:
         - targets: ['api-server:8000']
   ```
3. Load Grafana dashboards to monitor:
   - Request latency distributions (<200ms target).
   - CPU/Memory utilization of workers.
   - Redis active connections and Celery queue length.
