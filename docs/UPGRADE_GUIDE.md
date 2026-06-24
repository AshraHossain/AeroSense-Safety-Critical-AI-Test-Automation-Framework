# Upgrade Guide

How to upgrade from one version to the next.

## 0.1.x → 0.2.0

### Breaking Changes
- `@pytest.mark.requirement` format changed (no impact on tests)
- RTM export schema updated (old exports not compatible)

### Upgrade Steps

1. **Backup database**
   ```bash
   bash scripts/backup-postgres.sh
   ```

2. **Update code**
   ```bash
   git pull origin main
   git checkout v0.2.0
   ```

3. **Install dependencies**
   ```bash
   pip install -e . --upgrade
   ```

4. **Run migrations**
   ```bash
   alembic upgrade head
   ```

5. **Verify schema**
   ```bash
   alembic current
   ```

6. **Run tests**
   ```bash
   pytest --cov=src
   ```

7. **Restart services**
   ```bash
   # Local
   docker-compose restart app
   
   # Kubernetes
   kubectl rollout restart deployment/aerosense-app -n aerosense
   ```

### Rollback (if needed)

```bash
# Stop new version
kubectl scale deployment aerosense-app --replicas=0 -n aerosense

# Restore database backup
psql $DATABASE_URL < backup_YYYYMMDD_HHMMSS.sql

# Revert code
git checkout v0.1.0

# Downgrade migrations
alembic downgrade -1

# Restart old version
kubectl rollout undo deployment/aerosense-app -n aerosense
```

## General Upgrade Checklist

- [ ] Read CHANGELOG.md for breaking changes
- [ ] Backup database
- [ ] Pull latest code
- [ ] Install new dependencies
- [ ] Run migrations
- [ ] Test on staging first
- [ ] Verify alerts still work
- [ ] Monitor metrics for 1 hour post-upgrade
- [ ] Document any issues
