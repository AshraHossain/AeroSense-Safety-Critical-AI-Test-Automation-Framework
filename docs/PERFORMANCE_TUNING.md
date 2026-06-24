# Performance Tuning Guide

How to optimize the system for speed and throughput.

## Database Layer

### Indexing

```sql
-- Check slow queries
SELECT query, calls, mean_time FROM pg_stat_statements
WHERE mean_time > 100
ORDER BY mean_time DESC;

-- Add index if query scans full table
CREATE INDEX idx_audit_log_timestamp ON audit_log(timestamp);
CREATE INDEX idx_audit_log_model ON audit_log(ai_model);

-- Verify index is used
EXPLAIN ANALYZE SELECT * FROM audit_log WHERE timestamp > now() - interval '1 day';
```

### Query Optimization

```python
# BEFORE: N+1 query problem
for req in requirements:
    tests = db.query(Test).filter(Test.requirement_id == req.id).all()
    # Runs 1 + N queries

# AFTER: Join query
tests = db.query(Test).join(Requirement).filter(
    Requirement.id.in_([r.id for r in requirements])
).all()
# Runs 1 query
```

### Connection Pooling

See PGBOUNCER_CONFIG.md. Expected improvement: +20-50% throughput.

## Application Layer

### Caching

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_requirement(req_id):
    return db.query(Requirement).filter(Requirement.id == req_id).first()

# Cache invalidation on update
def update_requirement(req_id, data):
    get_requirement.cache_clear()
    # ... update ...
```

### Async I/O

```python
# BEFORE: Blocking calls
def generate_tests(srs):
    response = requests.post("https://api.anthropic.com/...", json=srs)
    tests = response.json()
    return tests

# AFTER: Async calls
async def generate_tests(srs):
    async with aiohttp.ClientSession() as session:
        async with session.post(...) as resp:
            tests = await resp.json()
            return tests
```

### Batch Operations

```python
# BEFORE: Insert 100 rows = 100 queries
for test in tests:
    db.add(test)
    db.commit()

# AFTER: Bulk insert = 1 query
db.bulk_insert_mappings(Test, tests)
db.commit()
```

## Frontend Layer (if applicable)

### Bundle Optimization

```bash
# Analyze bundle size
npm run build -- --analyze

# Remove unused code
npx knip --production

# Compress images
npx imagemin src/images/* --out-dir=dist/images
```

## Infrastructure

### Kubernetes Scaling

```bash
# Horizontal scaling: add more pods
kubectl scale deployment aerosense-app --replicas=5 -n aerosense

# Vertical scaling: increase resources per pod
kubectl set resources deployment aerosense-app \
  --limits=cpu=1000m,memory=1Gi \
  -n aerosense
```

### Load Balancing

Use round-robin across replicas (default K8s behavior).

### CDN

Cache static assets (if any):
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  annotations:
    nginx.ingress.kubernetes.io/cache-enable: "true"
```

## Monitoring Performance

### Prometheus Queries

```promql
# Request latency (p95)
histogram_quantile(0.95, http_request_duration_seconds)

# Throughput (RPS)
rate(http_requests_total[5m])

# Database query latency
histogram_quantile(0.95, db_query_duration_seconds)

# Cache hit rate
rate(cache_hits[5m]) / rate(cache_total[5m])
```

### Baseline Targets

| Metric | Target | Action if exceeded |
|--------|--------|-------------------|
| p95 latency | 500ms | Check slow query logs, add index |
| p99 latency | 1000ms | Increase pool size or scale pods |
| Throughput | 100 RPS | Check bottleneck (DB, CPU, network) |
| Error rate | < 0.1% | Investigate errors |

## Bottleneck Diagnosis

1. **Is it CPU?** → Optimize code or scale up
2. **Is it DB?** → Add index, optimize query, scale DB
3. **Is it memory?** → Check for leaks, reduce cache
4. **Is it network?** → Check for external API delays

```bash
# Check resource usage
kubectl top pods -n aerosense --containers

# Find CPU hotspot
python -m cProfile -s cumtime script.py

# Find memory leak
python -m tracemalloc script.py
```

## Quick Wins (low effort, high impact)

- [ ] Add index to frequently filtered columns
- [ ] Enable caching on read-heavy endpoints
- [ ] Batch insert operations
- [ ] Use connection pooling (PgBouncer)
- [ ] Enable gzip compression
- [ ] Remove debug logging in production
