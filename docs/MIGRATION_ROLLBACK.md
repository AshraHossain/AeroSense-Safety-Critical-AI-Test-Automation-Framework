# Database Migration Rollback Procedures

## Before Running Migrations

**Always backup first:**
```bash
# Backup current schema and data
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# Verify backup restored locally
psql $TEST_DATABASE < backup_*.sql
```

## Viewing Migrations

```bash
# Current revision
alembic current

# Revision history
alembic history

# Details of a migration
alembic show <revision>
```

## Rolling Back

### Option 1: Downgrade N Versions
```bash
# Undo last migration
alembic downgrade -1

# Undo last 3 migrations
alembic downgrade -3

# Undo to specific revision
alembic downgrade 058dc38
```

### Option 2: Targeted Downgrade
```bash
# Find target revision ID
alembic history | grep "add_column"

# Downgrade to that revision
alembic downgrade abc1234
```

## Testing Rollbacks

For each new migration, test rollback:
```bash
# On test database
alembic upgrade head
# (test the upgrade)
alembic downgrade -1
alembic upgrade head
# (verify idempotent)
```

## Emergency Rollback (Production)

If migration breaks production:

1. **Stop application** (pause Kubernetes deployment)
   ```bash
   kubectl scale deployment aerosense-app --replicas=0 -n aerosense
   ```

2. **Restore from backup**
   ```bash
   psql $DATABASE_URL < backup_YYYYMMDD_HHMMSS.sql
   ```

3. **Downgrade Alembic stamp**
   ```bash
   alembic stamp <previous_revision>
   ```

4. **Restart with previous code**
   ```bash
   git revert HEAD
   kubectl scale deployment aerosense-app --replicas=3 -n aerosense
   ```

5. **Investigate root cause**
   ```bash
   # Review migration file
   cat alembic/versions/NNN_*.py

   # Check if reversible (has downgrade() function)
   grep -A 20 "def downgrade" alembic/versions/NNN_*.py
   ```

## Non-Reversible Migrations

Some operations are irreversible:
- DROP COLUMN (data loss)
- DROP TABLE (data loss)
- ALTER TYPE (requires rewrite)

**Policy:** All migrations must be reversible. If not, that's a code review violation.

Check before merge:
```bash
# Must have downgrade() that exactly reverses upgrade()
alembic downgrade -1
alembic upgrade head
# (should be idempotent)
```

## Common Issues

### Migration Fails Partway
```bash
# Check Alembic stamp vs actual schema
alembic current  # What Alembic thinks is current
\dt audit_log    # psql: Check if table exists

# If mismatch, force stamp to match reality
alembic stamp <revision>
```

### Duplicate Rows After Downgrade
```bash
# If downgrade created duplicates, restore from backup instead
psql $DATABASE_URL < backup_before_failed_migration.sql
```

### Test Locally First
```bash
# Always test migration on copy of production data
pg_dump $PROD_DB | psql $LOCAL_TEST_DB
alembic upgrade head
alembic downgrade -1
# (verify no data loss)
```

## Backup Location

Backups stored in:
```
s3://aerosense-backups/postgres/
  └── backup_YYYYMMDD_HHMMSS.sql.gz
```

Retention: 30 days (automated by S3 lifecycle)
