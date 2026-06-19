# LifeOS AI – Backup & Disaster Recovery Runbook

This runbook outlines the data protection architecture, backup configurations, verification steps, and recovery procedures designed to satisfy our institutional availability SLA.

---

## 1. Disaster Recovery Parameters (SLA)

* **Recovery Point Objective (RPO):** **15 Minutes**
  * Maximum tolerable data loss duration. In case of primary database failure, the system must recover state from a snapshot or WAL log that is at most 15 minutes old.
* **Recovery Time Objective (RTO):** **30 Minutes**
  * Maximum tolerable downtime. From the moment an outage is detected, the database connection must be fully failed over and operational on replica/restored systems within 30 minutes.

---

## 2. Backup Strategy

1. **Continuous WAL Archiving (Point-in-Time Recovery):**
   * PostgreSQL Write-Ahead Logs (WAL) are shipped automatically to secure, encrypted S3 buckets every 60 seconds (using pgBackRest or Barman).
   * This guarantees that RPO <= 1 minute under ordinary operating conditions.
2. **Daily Logical Backups:**
   * Compressed PostgreSQL custom-format dumps (`pg_dump -F c`) are generated nightly at 02:00 AM UTC.
   * Stored in georedundant cold storage with a 30-day retention policy.
3. **Storage Security:**
   * All backups are encrypted at rest using AES-256 (KMS keys).
   * Access requires strict IAM roles with Multi-Factor Authentication (MFA) delete protection.

---

## 3. Monthly Restore Verification Procedure

To verify backup integrity and ensure the 30-minute RTO can be met, SRE/DevOps teams must perform a manual restore verification on the first Sunday of every month.

### Phase A: Generate Test Environment
1. Spin up an isolated staging/scratch database container matching production specs:
   ```bash
   docker run --name pg-restore-test -e POSTGRES_PASSWORD=test_restore_pwd -d postgres:16
   ```

### Phase B: Fetch and Verify Backup
1. Retrieve the latest nightly backup snapshot from S3 cold storage:
   ```bash
   aws s3 cp s3://lifeos-backups-prod/db_snapshots/daily-latest.dump ./latest.dump
   ```
2. Compute and cross-reference the checksum of the backup to verify payload integrity:
   ```bash
   sha256sum latest.dump
   ```

### Phase C: Execute Restore
1. Restore the schema and data into the test container:
   ```bash
   pg_restore -h localhost -U postgres -d postgres -v ./latest.dump
   ```
2. Audit the timing: The restore command *must* execute within 15 minutes for current database volumes to satisfy the 30-minute RTO buffer.

### Phase D: Assertive Testing & Logging
1. Run row-count comparisons and spot checks on primary tables (`users`, `tasks`, `trading_journal`):
   ```sql
   SELECT COUNT(*), MAX(created_at) FROM tasks;
   ```
2. Validate that the application boots successfully using the restored schema.
3. **Log the results** in the verification register (`docs/backup_restore.md` updates or incident logs):
   * **Backup Created:** Time & Date of snapshot.
   * **Backup Verified:** SHA256 matches S3 metadata.
   * **Restore Verified:** All checks passed, row counts match.
