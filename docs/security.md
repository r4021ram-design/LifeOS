# LifeOS AI – Production Security Checklist

This document details the critical security implementations and audit checklists verified for deployment.

---

## 1. Authentication & Session Security

- [x] **JWT Token Encryption:** Signed with `HS256` using a cryptographically random `SECRET_KEY` loaded exclusively from environment variables.
- [x] **Separation of Concerns:** Separate Access Token (short expiration, 1 hour) and Refresh Token (7 days, containing `{"refresh": true}` payload) preventing session replay attacks.
- [x] **Password Storage:** One-way hashing using `bcrypt` (via passlib context manager) with auto-generated salt and work factor configurations.

---

## 2. API Guarding & Network Security

- [x] **Rate Limiting:** Guard critical routes (e.g. `/auth/login`, `/auth/signup`) using middleware or redis-based access thresholds.
- [x] **CORS Configuration:** Limit allow-origins in production configurations to the exact front-end domain (e.g., `https://app.lifeos-ai.com`), avoiding wildcard `*` headers.
- [x] **CSRF & XSS Protection:** Secure all browser local-storage actions and cookies, and utilize strict JSON-only schemas for API inputs to prevent injection.

---

## 3. Database & Layer Protections

- [x] **SQL Injection Prevention:** All queries built using SQLAlchemy 2.0 ORM expressions which parameterize inputs automatically. Avoid raw SQL strings.
- [x] **Input Validation:** Enforce strict field constraints (length, characters, email format) using Pydantic validation schemas in `schemas/schemas.py`.
- [x] **Least Privilege DB Role:** Connect FastAPI using a postgres role limited strictly to DDL/DML on the `lifeos` schema (no superuser access).
