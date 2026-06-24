# API Rate Limits

Rate limiting prevents abuse and ensures fair resource allocation.

## Per-Endpoint Limits

| Endpoint | Limit | Window | Notes |
|----------|-------|--------|-------|
| `/mcp/generate_tests` | 10 req/min | 60s | Expensive LLM call |
| `/mcp/hitl/submit` | 30 req/min | 60s | Action submission |
| `/mcp/hitl/approve` | 50 req/min | 60s | Fast human review |
| `/mcp/audit` | 100 req/min | 60s | Read-only query |
| `/health` | Unlimited | - | Health checks exempt |

## Client Behavior

### Handling 429 (Rate Limited)

```bash
# HTTP 429 response
HTTP/1.1 429 Too Many Requests
Retry-After: 30

# Exponential backoff
attempt=1
while [ $attempt -le 5 ]; do
  response=$(curl -s -w "\n%{http_code}" $URL)
  code=$(echo "$response" | tail -1)
  
  if [ "$code" == "429" ]; then
    sleep=$((2 ** $attempt))
    echo "Rate limited. Waiting ${sleep}s..."
    sleep $sleep
    attempt=$((attempt + 1))
  else
    echo "$response"
    break
  fi
done
```

### Optimal Request Pattern

- Batch requests when possible
- Space requests evenly over time
- Don't hammer endpoints in tight loops
- Use webhooks (future) instead of polling

## Tuning

Limits are per-endpoint and per-client (IP-based). To adjust:

```python
# src/mcp_server/server.py
rate_limiter.set_limit(
  endpoint="/mcp/generate_tests",
  requests=20,        # new limit
  window_seconds=60
)
```

## Monitoring

Check current rate limit usage:

```bash
# Check prometheus metric
curl http://localhost:9090/api/v1/query?query=rate_limit_exceeded_total

# If spike detected, check:
# 1. Load test running?
# 2. Legitimate traffic surge?
# 3. DOS attack? (Block IPs in firewall)
```

## Future Enhancements

- Per-user limits (via JWT claims)
- Quota allowances (pay for higher limits)
- Sliding window instead of fixed window
- Distributed rate limiting (Redis) for multi-instance
