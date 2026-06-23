# Cost Estimation (AWS)

## Per-Month Breakdown

### Compute (EKS)
- Node: 2 × t3.medium (burstable, 2 vCPU, 4GB RAM)
- Cost: 2 × $0.0416/hr × 730hrs = **$60.74/month**
- HPA scales 2-10 replicas, average 3-4 during business hours

### PostgreSQL (RDS)
- Instance: db.t3.micro (1 vCPU, 1GB RAM, 20GB storage)
- Cost: $0.017/hr × 730hrs + storage = **$45-60/month**
- Alternative: Self-managed (included in EKS node cost)

### Network
- Data transfer out: ~100GB/month @ $0.09/GB = **$9/month**
- LoadBalancer: $0.025/hr × 730hrs = **$18/month**

### Monitoring
- Prometheus (self-hosted on node): **Free**
- Grafana Cloud: $29/month (optional; can self-host)

### Claude API Calls
- Estimated: 100 test generations/month
- Cost per call: ~$0.01 (Sonnet 4.6 small tokens)
- Monthly: 100 × $0.10 (avg) = **$10/month**

---

## Total Estimate: **$142-180/month** (self-hosted monitoring)

### Cost Optimization Strategies

1. **Spot Instances:** Save 70% on compute
   - Convert to spot: $60 → $18/month
   - New total: ~**$65-90/month**

2. **Vertical Scaling:** Use t4g.small instead of t3.medium
   - Saves: $10-15/month

3. **Reserved Instances:** 1-year commitment saves 30%
   - Saves: $20-30/month

4. **Consolidate:** Run postgres on EKS nodes instead of RDS
   - Saves: $45-60/month

---

## Scaling Costs

- 10x traffic: Add 3-4 more nodes (~$90-120/month additional)
- 100x traffic: Auto-scale design holds; add load balancing (~$50-100/month)

## Break-Even

- Break-even with managed services (Firebase, Aurora Serverless): **5-10x load**
- Self-hosted remains most cost-effective at current scale

---

## Recommendations

1. **Start:** Self-hosted EKS with spot instances (~$65/month)
2. **Scale:** Add reserved instances at 2x load
3. **Mature:** Consider serverless (AppRunner, Aurora Serverless) at 10x+ load
