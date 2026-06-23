# Deployment Guide

## Local Development

```bash
# 1. Setup environment
bash scripts/setup.sh

# 2. Start services
docker-compose up -d

# 3. Verify health
curl http://localhost:8000/health

# 4. Run tests
pytest --cov=src
```

## Kubernetes Deployment

### Prerequisites
- K8s cluster (1.20+)
- `helm` 3.0+
- External secrets operator (optional, for AWS Secrets Manager)

### Install

```bash
# 1. Create namespace
kubectl create namespace aerosense

# 2. Create secrets
kubectl create secret generic aerosense-secrets \
  --from-literal=postgres-password=<secret> \
  --from-literal=anthropic-api-key=<key> \
  -n aerosense

# 3. Install Helm chart
helm install aerosense ./helm \
  --namespace aerosense \
  --values helm/values.yaml

# 4. Verify rollout
kubectl rollout status deployment/aerosense-app -n aerosense
```

### Scaling

HPA auto-scales from 2 to 10 replicas based on CPU/memory:

```bash
# Check HPA status
kubectl get hpa -n aerosense

# Manual scaling
kubectl scale deployment aerosense-app --replicas=5 -n aerosense
```

## Database Migrations

Alembic handles schema versioning:

```bash
# Current revision
alembic current

# Upgrade to latest
alembic upgrade head

# Downgrade
alembic downgrade -1

# Create new migration
alembic revision --autogenerate -m "add column"
```

## Monitoring

### Prometheus
```bash
# Port-forward for local access
kubectl port-forward -n aerosense svc/prometheus 9090:9090

# Query: http://localhost:9090
```

### Grafana
```bash
# Port-forward
kubectl port-forward -n aerosense svc/grafana 3000:3000

# Login: admin/admin (change on first login)
# Import dashboard: monitoring/grafana-dashboard.json
```

## Load Testing

### K6 (local)
```bash
k6 run load-tests/endpoints.js
```

### Against K8s cluster
```bash
k6 run load-tests/endpoints.js \
  -e BASE_URL=https://aerosense.example.com
```

## Chaos Engineering

### Network latency
```bash
kubectl apply -f k8s/chaos/network-chaos.yaml
```

### Pod disruption
```bash
kubectl apply -f k8s/chaos/pod-disruption-budget.yaml
```

## Troubleshooting

- Check logs: `kubectl logs -n aerosense deployment/aerosense-app -f`
- Debug pod: `kubectl exec -it -n aerosense pod/aerosense-app-xxx -- /bin/sh`
- Port-forward: `kubectl port-forward -n aerosense svc/aerosense-app 8000:8000`

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues.
