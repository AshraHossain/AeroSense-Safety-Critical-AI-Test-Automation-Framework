#!/bin/bash
# Convenient port-forward shortcuts for Kubernetes services

set -e

NAMESPACE="aerosense"

case "${1:-help}" in
  prometheus)
    echo "🔗 Forwarding Prometheus: http://localhost:9090"
    kubectl port-forward -n $NAMESPACE svc/prometheus 9090:9090
    ;;
  grafana)
    echo "🔗 Forwarding Grafana: http://localhost:3000 (admin/admin)"
    kubectl port-forward -n $NAMESPACE svc/grafana 3000:3000
    ;;
  app)
    echo "🔗 Forwarding App: http://localhost:8000"
    kubectl port-forward -n $NAMESPACE svc/aerosense-app 8000:8000
    ;;
  postgres)
    echo "🔗 Forwarding Postgres: localhost:5432"
    kubectl port-forward -n $NAMESPACE svc/postgres 5432:5432
    ;;
  all)
    echo "🔗 Forwarding all services..."
    kubectl port-forward -n $NAMESPACE svc/prometheus 9090:9090 &
    kubectl port-forward -n $NAMESPACE svc/grafana 3000:3000 &
    kubectl port-forward -n $NAMESPACE svc/aerosense-app 8000:8000 &
    kubectl port-forward -n $NAMESPACE svc/postgres 5432:5432 &
    echo "All services forwarded. Press Ctrl+C to stop."
    wait
    ;;
  *)
    echo "Port-forward shortcuts for Kubernetes services"
    echo ""
    echo "Usage: $0 [service]"
    echo ""
    echo "Services:"
    echo "  prometheus   - Prometheus metrics (http://localhost:9090)"
    echo "  grafana      - Grafana dashboards (http://localhost:3000)"
    echo "  app          - App API (http://localhost:8000)"
    echo "  postgres     - PostgreSQL (localhost:5432)"
    echo "  all          - Forward all services"
    echo "  help         - Show this help message"
    echo ""
    echo "Example:"
    echo "  $0 grafana   # Open Grafana dashboards"
    echo "  $0 all       # Forward all services in background"
    ;;
esac
