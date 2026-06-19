# LifeOS AI – Secrets Management & Rotation Runbook

This document details the security procedures for storing, accessing, and rotating sensitive application keys and database passwords.

---

## 1. Storage Standards

All production secrets must NEVER be committed to Git. They are managed as follows:
- **Cloud Deployments:** Configured as environment variables injected at runtime, sourced from secure key managers (e.g. AWS Secrets Manager, HashiCorp Vault, or GitHub Repository Secrets for CI).
- **Local Development:** Maintained in the git-ignored `backend/.env` file.

---

## 2. Inventory of Critical Secrets

The following environment variables require strict management and encryption:
- `SECRET_KEY`: Used for JWT authentication payload signatures.
- `DATABASE_URL`: Connection credentials to PostgreSQL production cluster.
- `REDIS_URL`: Credentials for Redis cache and celery broker.
- `OPENAI_API_KEY` & `GEMINI_API_KEY`: API access tokens.
- `KOTAK_API_KEY` & `FYERS_API_KEY`: Broker connection secrets.
- `SMTP_PASSWORD`: Credentials for sending alert emails.

---

## 3. Secret Rotation Procedures

Critical keys must be rotated **every 90 days** or immediately upon suspecting a leak.

### Procedure A: Rotating JWT `SECRET_KEY`
1. Generate a new cryptographically random 32-byte key:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
2. Update the environment configuration:
   * Inject the new token as `SECRET_KEY` value in production configurations.
3. Perform a rolling restart of uvicorn FastAPI processes:
   * Note: This will invalidate all active user sessions, forcing users to re-login.

### Procedure B: Rotating Database Password
1. Generate a new password for the database user:
   ```sql
   ALTER USER lifeos_db_user WITH PASSWORD 'new_secure_pwd_xyz';
   ```
2. Update the secret manager / environment configurations:
   * Modify the password in the connection string: `DATABASE_URL=postgresql+psycopg2://lifeos_db_user:new_secure_pwd_xyz@pg-host:5432/dbname`.
3. Perform a zero-downtime rolling restart of backend containers:
   * The application uses connection pooling and will seamlessly reconnect using the updated connection strings.
