# Disaster Recovery Plan

How to recover from catastrophic failures.

## Recovery Time Objectives (RTO) & Recovery Point Objectives (RPO)

| Scenario | RTO | RPO | Action |
|----------|-----|-----|--------|
| Database corrupted | 1 hour | 24 hours | Restore from backup |
| Entire region down | 4 hours | 1 hour | Failover to DR region |
| Data center fire | 8 hours | 1 day | Restore to cloud |

## Backup Strategy

### Database Backups

```bash
# Automated daily backups
bash scripts/backup-postgres.sh

# Stored in S3
s3://aerosense-backups/postgres/backup_YYYYMMDD_HHMMSS.sql.gz

# Retention: 30 days (automated cleanup)
```

### Code Backups

```bash
# All code in git (primary backup)
https://github.com/AshraHossain/aerosense-testforge

# Tag releases
git tag -a v0.1.0 -m "Release 0.1.0"
git push origin v0.1.0
```

### Configuration Backups

```bash
# Export Kubernetes secrets
kubectl get secret -n aerosense -o yaml > backup-secrets.yaml

# Export ConfigMaps
kubectl get configmap -n aerosense -o yaml > backup-configmaps.yaml

# Store securely (encrypted)
```

## Disaster Scenarios

### Scenario 1: Database Corruption

**Symptoms:** Queries fail, audit log shows corrupted records

**Recovery (1 hour):**

```bash
# 1. Stop application (prevent further writes)
kubectl scale deployment aerosense-app --replicas=0 -n aerosense

# 2. Find latest good backup
ls -ltr ~/backups/backup_*.sql.gz | tail -5

# 3. Restore on test database first
createdb aerosense-test
gunzip < backup_20260623_120000.sql.gz | psql aerosense-test

# 4. Verify data integrity
psql aerosense-test -c "SELECT count(*) FROM audit_log;"

# 5. Restore production database
gunzip < backup_20260623_120000.sql.gz | psql $DATABASE_URL

# 6. Verify stamp in alembic
alembic current

# 7. Restart application
kubectl scale deployment aerosense-app --replicas=3 -n aerosense

# 8. Verify health
curl https://aerosense.example.com/health
```

**Prevention:**
- Automated backups (daily)
- Backup integrity tests (weekly)
- Primary key constraints
- Foreign key constraints
- Triggers for audit trail immutability

### Scenario 2: Complete Data Loss

**Symptoms:** All postgres data gone, backup needed

**Recovery (depends on backup age):**

```bash
# 1. Verify backup exists and is valid
gunzip -t backup_YYYYMMDD_HHMMSS.sql.gz

# 2. Create new database
createdb aerosense-recovery

# 3. Restore from backup
gunzip < backup_YYYYMMDD_HHMMSS.sql.gz | psql aerosense-recovery

# 4. Verify completeness
psql aerosense-recovery -c "SELECT count(*) FROM audit_log;"

# 5. Swap with production
# Stop app, drop old DB, rename recovery to production
```

**Prevention:**
- Daily backups (24-hour RPO)
- Backup to multiple locations (local + S3 + cloud)
- Backup encryption (AES-256)
- Monthly restore drills

### Scenario 3: Kubernetes Cluster Failure

**Symptoms:** All pods down, no way to recover

**Recovery (2-4 hours):**

```bash
# 1. Verify cluster is truly gone
kubectl cluster-info  # times out

# 2. Create new cluster
gcloud container clusters create aerosense-recovery \
  --zone us-central1-a \
  --num-nodes 3

# 3. Deploy application
kubectl create namespace aerosense
helm install aerosense ./helm -n aerosense

# 4. Restore database (from backup)
bash scripts/backup-postgres.sh  # restore mode

# 5. Verify services
kubectl get pods -n aerosense
curl https://aerosense.example.com/health
```

**Prevention:**
- Multi-region deployment (active-passive or active-active)
- Terraform/Helm as infrastructure-as-code (reproducible)
- Regular disaster recovery drills

### Scenario 4: Ransomware/Malicious Deletion

**Symptoms:** Data encrypted or deleted, ransom demand

**Recovery (6 hours):**

```bash
# 1. Isolate affected systems immediately
kubectl delete deployment aerosense-app -n aerosense
# Don't power off (may be in recovery state)

# 2. Notify security team
# Don't pay ransom

# 3. Restore from verified clean backup
# Use backup from BEFORE infection date

# 4. Change all credentials
# Rotate: ANTHROPIC_API_KEY, database passwords, SSH keys

# 5. Audit for breach
# Check logs: who accessed what, when
# Check for exfiltration

# 6. Revert to known-good code version
git checkout v0.1.0
kubectl apply -f k8s/
```

**Prevention:**
- Backup encryption (prevents reading)
- Immutable backups (append-only, can't delete)
- Least privilege access (limit who can modify backups)
- Monitoring for unusual activity (large data transfers)

## Testing Disaster Recovery

**Monthly drill:** Restore database from backup to test environment

```bash
#!/bin/bash
# restore-drill.sh - Monthly DR drill

echo "Starting DR drill..."

# 1. Get latest backup
BACKUP=$(ls -1t ~/backups/*.sql.gz | head -1)

# 2. Restore to test database
createdb aerosense-test
gunzip < $BACKUP | psql aerosense-test

# 3. Verify data integrity
TEST_COUNT=$(psql aerosense-test -t -c "SELECT count(*) FROM audit_log;")
PROD_COUNT=$(psql $DATABASE_URL -t -c "SELECT count(*) FROM audit_log;")

if [ "$TEST_COUNT" -eq "$PROD_COUNT" ]; then
  echo "✓ Backup integrity verified"
  echo "Row count: $TEST_COUNT (matches production)"
else
  echo "❌ Backup integrity check FAILED"
  exit 1
fi

# 4. Clean up
dropdb aerosense-test

# 5. Log success
date >> /var/log/dr-drills.log
echo "DR drill completed successfully" >> /var/log/dr-drills.log
```

Schedule: Cron job at 2am monthly
```bash
0 2 1 * * /usr/local/bin/restore-drill.sh
```

## Communication During Disaster

1. **Declare incident** (INCIDENT_ESCALATION.md)
2. **Notify customers** (status page)
3. **Hourly updates** to stakeholders
4. **Post-recovery** debriefing within 24 hours

## Rollback Plan

If recovery fails or causes new issues:

```bash
# Keep old infrastructure running until new is verified
kubectl set image deployment/aerosense-app \
  aerosense-app=aerosense:v0.1.0 \
  -n aerosense

# Verify old version works
curl https://aerosense.example.com/health

# Once stable, document what went wrong
# Update recovery procedures
# Re-train team
```

## Documentation

Keep updated:
- [ ] Backup location documented
- [ ] Recovery procedure tested
- [ ] Credentials stored securely
- [ ] Team trained on recovery
- [ ] Postmortem from last disaster reviewed
