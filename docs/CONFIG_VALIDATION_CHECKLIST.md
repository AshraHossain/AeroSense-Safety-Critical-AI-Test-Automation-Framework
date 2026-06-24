# Configuration Validation Checklist

Pre-deployment verification for production environment.

## Before Deploying to Production

Run this checklist to catch configuration issues early.

### Secrets & Credentials

- [ ] `ANTHROPIC_API_KEY` set and valid (test with API call)
- [ ] `DATABASE_URL` points to production postgres (not dev)
- [ ] Database credentials have minimal required permissions
- [ ] No secrets in `.env` file tracked in git (should be .gitignored)
- [ ] All secrets rotated within last 90 days
- [ ] Backup credentials stored in secure location

### Database

- [ ] Database exists and is accessible
- [ ] Postgres version >= 12
- [ ] Backups configured (daily minimum)
- [ ] `max_connections` set to accommodate pool size
- [ ] SSL/TLS enabled for remote connections
- [ ] `shared_preload_libraries` includes `pg_stat_statements` (for monitoring)

### Application

- [ ] `LOG_LEVEL` set to `warn` (not `debug`)
- [ ] `CLAUDE_MODEL` pinned to specific version (not `latest`)
- [ ] `PORT` set to standard port (8000)
- [ ] All required environment variables present
- [ ] Application starts without errors: `python -m src.main`
- [ ] Health check responds: `curl http://localhost:8000/health`

### Kubernetes (if deploying to K8s)

- [ ] Namespace exists: `kubectl get ns aerosense`
- [ ] ConfigMap populated: `kubectl get cm -n aerosense`
- [ ] Secrets populated: `kubectl get secret -n aerosense`
- [ ] Image exists in registry and can be pulled
- [ ] Resource limits set (CPU, memory)
- [ ] Readiness probe configured
- [ ] Liveness probe configured
- [ ] PVC exists for postgres (if using StatefulSet)
- [ ] Ingress configured with TLS cert

### Monitoring

- [ ] Prometheus scrape configs in place
- [ ] Alert rules configured (RUNBOOKS.md)
- [ ] Grafana dashboards imported
- [ ] Oncall rotation configured
- [ ] Slack webhook configured for alerts

### Security

- [ ] HTTPS/TLS enabled (cert valid, not self-signed)
- [ ] Security headers configured (CSP, HSTS, X-Frame-Options)
- [ ] Rate limiting enabled
- [ ] Request signing enabled (HMAC validation)
- [ ] No debug endpoints exposed (`/debug`, `/admin`)
- [ ] Firewall rules restrict access appropriately

### Backups & Disaster Recovery

- [ ] Database backup script running
- [ ] Backup retention policy in place
- [ ] Restore procedure tested (restore latest backup to test DB)
- [ ] Backup encrypted and stored off-site

### Documentation

- [ ] Runbooks in place (RUNBOOKS.md)
- [ ] Escalation chain documented (INCIDENT_ESCALATION.md)
- [ ] Architecture diagram up-to-date (ARCHITECTURE.md)
- [ ] Postmortem template ready (POSTMORTEM_TEMPLATE.md)

### Testing

- [ ] All tests pass: `pytest --cov=src`
- [ ] Coverage >= 80%: `pytest --cov-report=term-missing`
- [ ] Load test completed: `k6 run load-tests/endpoints.js`
- [ ] SLO targets validated under load

### Deployment

- [ ] Rollback plan documented
- [ ] Deployment scheduled during low-traffic window
- [ ] Team notified of deployment
- [ ] On-call engineer standing by

## Pre-Deployment Test Procedure

```bash
# 1. Verify environment
env | grep -E "DATABASE_URL|ANTHROPIC_API_KEY|LOG_LEVEL|CLAUDE_MODEL"

# 2. Test database connectivity
psql $DATABASE_URL -c "SELECT version();"

# 3. Test API key
python -c "
import anthropic
client = anthropic.Anthropic(api_key='$ANTHROPIC_API_KEY')
message = client.messages.create(model='claude-opus-4-8', max_tokens=10, messages=[{'role': 'user', 'content': 'hi'}])
print('✓ API key valid')
"

# 4. Run tests
pytest --cov=src --cov-report=term-missing -q

# 5. Check coverage
if grep "FAILED" coverage-report.txt; then echo "❌ Coverage < 80%"; exit 1; fi
echo "✓ Coverage >= 80%"

# 6. Start service and verify health
python -m src.main &
sleep 5
curl http://localhost:8000/health || exit 1
kill %1
echo "✓ Service healthy"

# 7. Deploy
kubectl apply -f k8s/
kubectl rollout status deployment/aerosense-app -n aerosense

# 8. Verify in production
curl https://aerosense.example.com/health
echo "✓ Production deployment successful"
```

## Post-Deployment

- [ ] Metrics flowing into Prometheus
- [ ] Alerts configured and testing
- [ ] Logs flowing into aggregator
- [ ] Health check passing
- [ ] Sample request successful
- [ ] Monitor for 30 minutes before marking complete
