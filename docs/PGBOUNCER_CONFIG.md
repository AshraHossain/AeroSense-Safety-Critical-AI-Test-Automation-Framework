# PgBouncer Configuration

Connection pooling for PostgreSQL scalability.

## Why PgBouncer?

- **Limit database connections** (postgres default: 100, expensive)
- **Reduce connection overhead** (establish once, reuse many times)
- **Handle traffic spikes** (queue excess requests, don't overwhelm DB)
- **Transparent to app** (app connects to PgBouncer like a normal postgres)

## Installation (Docker)

```dockerfile
FROM pgbouncer:1.21-alpine

COPY pgbouncer.ini /etc/pgbouncer/
COPY userlist.txt /etc/pgbouncer/

EXPOSE 6432

CMD ["pgbouncer", "/etc/pgbouncer/pgbouncer.ini"]
```

## Configuration (pgbouncer.ini)

```ini
[databases]
aerosense = host=postgres dbname=aerosense

[pgbouncer]
; Pool mode: session, transaction, statement
pool_mode = transaction

; Connection limits
max_client_conn = 1000
default_pool_size = 20
min_pool_size = 5
reserve_pool_size = 5
reserve_pool_timeout = 3

; Timeouts
server_lifetime = 3600
server_idle_in_transaction_session_timeout = 600
query_wait_timeout = 120

; Logging
admin_users = postgres
stats_users = postgres

; Security
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt
```

## User List (userlist.txt)

```
"postgres" "password_hash"
"app_user" "password_hash"
```

Generate hash:
```bash
python3 -c "import hashlib; print(hashlib.md5(b'password').hexdigest())"
```

## Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pgbouncer
spec:
  replicas: 1
  selector:
    matchLabels:
      app: pgbouncer
  template:
    metadata:
      labels:
        app: pgbouncer
    spec:
      containers:
      - name: pgbouncer
        image: pgbouncer:1.21-alpine
        ports:
        - containerPort: 6432
        env:
        - name: PGBOUNCER_DATABASES
          value: "aerosense=host=postgres dbname=aerosense"
        volumeMounts:
        - name: config
          mountPath: /etc/pgbouncer
      volumes:
      - name: config
        configMap:
          name: pgbouncer-config
```

## Monitoring

```bash
# Connect to admin console
psql -h localhost -p 6432 -U postgres -d pgbouncer -c "SHOW STATS"

# Pool status
psql -h localhost -p 6432 -U postgres -d pgbouncer -c "SHOW POOLS"

# Active connections
psql -h localhost -p 6432 -U postgres -d pgbouncer -c "SHOW CLIENTS"
```

## Prometheus Metrics

Add to pgbouncer:

```ini
[pgbouncer]
stats_period = 60
```

Then scrape `/admin` endpoint (custom prometheus exporter needed).

## Tuning

| Scenario | Config |
|----------|--------|
| High latency | Increase `default_pool_size` |
| Connection pool exhausted | Increase `max_client_conn` |
| Idle connections | Decrease `reserve_pool_timeout` |
| Transaction conflicts | Use `pool_mode = session` |

## App Integration

Update `DATABASE_URL`:

```bash
# Before (direct to postgres)
postgresql://postgres:password@postgres:5432/aerosense

# After (via pgbouncer)
postgresql://postgres:password@pgbouncer:6432/aerosense
```

## Performance Impact

- Latency: -5% to -15% (connection reuse)
- Throughput: +20% to +50% (connection pooling)
- Memory: +50MB (configurable)

## Troubleshooting

**"Too many connections"**
```bash
# Increase max_client_conn or default_pool_size
# Or reduce pool_mode overhead (use transaction mode)
```

**"Connection idle timeout"**
```bash
# Increase server_idle_in_transaction_session_timeout
# Or commit transactions faster
```
