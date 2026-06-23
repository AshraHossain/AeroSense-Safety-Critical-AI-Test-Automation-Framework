# Troubleshooting Guide

## Common Issues

### PostgreSQL Connection Refused
**Error:** `could not connect to server: Connection refused`

**Fix:**
```bash
# Verify postgres running
docker-compose ps

# Restart
docker-compose restart postgres

# Check logs
docker-compose logs postgres
```

### Rate Limiter Blocking Requests (429)
**Error:** HTTP 429 Too Many Requests

**Fix:**
```bash
# Check limits in code
grep -n "set_limit" src/middleware/rate_limiter.py

# Increase limit
# In src/mcp_server/server.py, adjust rate_limiter.limits
```

### Tests Failing with "Database unavailable"
**Error:** `psycopg2.OperationalError: could not connect to server`

**Fix:**
```bash
# Skip integration tests (require postgres)
pytest -k "not integration"

# Or start postgres
docker-compose up postgres -d
```

### Health Check Fails (503)
**Error:** GET /health returns 503

**Fix:**
```bash
# Check postgres connectivity
docker-compose logs app | grep "Database"

# Verify DATABASE_URL in .env
cat .env | grep DATABASE_URL
```

### Helm Deployment Stuck in Pending
**Error:** `kubectl get pods` shows `Pending`

**Fix:**
```bash
# Check events
kubectl describe pod <pod-name> -n aerosense

# Check resources
kubectl top nodes

# Verify secrets
kubectl get secret -n aerosense
```

### Coverage Below 90%
**Error:** `FAILED Required test coverage of 90.0% not reached`

**Fix:**
```bash
# See missing coverage
pytest --cov=src --cov-report=term-missing

# Add tests for uncovered lines
# Focus on src/main.py, src/startup.py, src/telemetry.py
```

### OpenAPI Spec Not Updated
**Fix:**
```bash
# FastAPI auto-generates; refresh by running server
python -m src.main &
curl http://localhost:8000/openapi.json > openapi.json
```

### K6 Load Test Fails
**Error:** `error: connection refused`

**Fix:**
```bash
# Verify app running
curl http://localhost:8000/health

# Check K6 BASE_URL
grep BASE_URL load-tests/endpoints.js
```

## Performance Issues

### High Latency (>500ms p95)
**Check:**
```bash
# 1. Database slow queries
kubectl logs -n aerosense deployment/aerosense-app | grep "slow query"

# 2. HPA scaling
kubectl get hpa -n aerosense

# 3. CPU/memory usage
kubectl top pods -n aerosense
```

### High Memory Usage
```bash
# Check for leaks
kubectl describe pod <pod-name> -n aerosense

# Restart pod
kubectl rollout restart deployment/aerosense-app -n aerosense
```

## Monitoring

### Check Metrics
```bash
# Prometheus queries
curl 'http://localhost:9090/api/v1/query?query=http_request_duration_seconds'

# Grafana dashboard
http://localhost:3000 (admin/admin)
```

### Check Alerts
```bash
# Active alerts
curl http://localhost:9090/api/v1/rules | grep active
```

## Getting Help

1. Check logs: `kubectl logs -n aerosense deployment/aerosense-app -f`
2. Read [ARCHITECTURE.md](ARCHITECTURE.md)
3. See [DEPLOYMENT.md](DEPLOYMENT.md)
4. File issue: https://github.com/AshraHossain/aerosense-testforge/issues
