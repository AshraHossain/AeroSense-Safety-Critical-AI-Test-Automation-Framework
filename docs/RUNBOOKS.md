# Runbooks: Incident Response

## High Latency (p95 > 500ms)

1. **Check current metrics**
   ```bash
   kubectl port-forward -n aerosense svc/prometheus 9090:9090
   # Query: histogram_quantile(0.95, http_request_duration_seconds)
   ```

2. **Diagnose**
   - Database slow? `kubectl logs -n aerosense deployment/aerosense-app | grep "slow query"`
   - CPU throttled? `kubectl top pods -n aerosense`
   - Memory pressure? `kubectl top nodes`

3. **Fix**
   - Database: Scale postgres replicas or optimize queries
   - CPU: Increase pod resources or scale horizontally (HPA)
   - Memory: Check for leaks, reduce cache TTL

4. **Verify**
   ```bash
   make load-test  # Run load test to confirm latency recovered
   ```

## High Error Rate (> 0.1%)

1. **Check error logs**
   ```bash
   kubectl logs -n aerosense deployment/aerosense-app -f | grep ERROR
   ```

2. **Common causes**
   - Rate limiting (429): Check `/mcp/hitl/submit` endpoint
   - Database down: Check postgres pod status
   - API key expired: Check ANTHROPIC_API_KEY secret
   - Disk full: Check pod storage usage

3. **Fix**
   - Rate limiting: Increase limits in `src/middleware/rate_limiter.py`
   - Database: Restart postgres pod
   - API key: Update secret and restart pods
   - Disk: Cleanup old audit logs or scale PVC

## Pod Crash Loop

1. **Check pod status**
   ```bash
   kubectl describe pod <pod-name> -n aerosense
   kubectl logs <pod-name> -n aerosense --previous
   ```

2. **Common causes**
   - OOMKilled: Memory leak or insufficient limits
   - CrashLoopBackOff: Code error or missing dependency
   - ImagePullBackOff: Docker image not found

3. **Fix**
   - OOMKilled: Increase memory limit or fix leak
   - CrashLoopBackOff: Check deployment logs, rollback if needed
   - ImagePullBackOff: Verify docker image exists in registry

## Database Connection Pool Exhausted (> 15/20 connections)

1. **Check connections**
   ```bash
   psql $DATABASE_URL -c "SELECT count(*) FROM pg_stat_activity;"
   ```

2. **Common causes**
   - Slow queries holding connections
   - Connection leak in app
   - Too many pod replicas

3. **Fix**
   - Kill idle connections: `psql -c "SELECT pg_terminate_backend(pid) ..."`
   - Scale down pods: `kubectl scale deployment aerosense-app --replicas=2 -n aerosense`
   - Review slow queries in postgres logs

## Audit Log Corruption (rows missing)

1. **Check immutability**
   ```bash
   psql $DATABASE_URL -c "SELECT count(*) FROM audit_log;"
   # Compare with backup count
   ```

2. **This should NOT happen** (triggers prevent UPDATE/DELETE)
   - If it did, someone bypassed the DB layer (investigate security breach)

3. **Recovery**
   - Restore from backup (see MIGRATION_ROLLBACK.md)
   - Alert security team
   - Review audit logs for who accessed DB

## Kubernetes Node Failure

1. **Check node status**
   ```bash
   kubectl get nodes
   kubectl describe node <node-name>
   ```

2. **Actions**
   - Cordon node: `kubectl cordon <node-name>`
   - Drain workloads: `kubectl drain <node-name> --ignore-daemonsets`
   - Replace node (varies by cloud provider)

3. **Pod Disruption Budget ensures** at least 1 pod stays running

## Memory Leak Suspected

1. **Check memory growth**
   ```bash
   kubectl top pods -n aerosense --containers
   # Monitor over 30 minutes
   ```

2. **Collect heap dump**
   ```bash
   python -m pdb <running-process>
   import tracemalloc
   tracemalloc.start()
   # Run workload, then dump()
   ```

3. **Fix**
   - Review recent code changes for unclosed resources
   - Check for circular references or unbounded data structures
   - Deploy fix and restart pods

## Unable to Deploy (Helm Error)

1. **Check helm status**
   ```bash
   helm status aerosense -n aerosense
   helm history aerosense -n aerosense
   ```

2. **Rollback to last working version**
   ```bash
   helm rollback aerosense -n aerosense
   ```

3. **Debug**
   ```bash
   helm template aerosense ./helm | kubectl apply --dry-run=client -f -
   ```

## Escalation

For critical incidents:
1. Page oncall: PagerDuty or similar
2. Declare incident in #incidents Slack channel
3. Follow postmortem template (docs/POSTMORTEM_TEMPLATE.md)
