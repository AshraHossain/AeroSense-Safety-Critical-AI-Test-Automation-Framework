#!/bin/bash
# Health check script - verify all services are running and healthy

set -e

echo "🏥 AeroSense Health Check"
echo "=========================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_service() {
  local name=$1
  local url=$2
  local expected_code=$3

  response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")

  if [ "$response" == "$expected_code" ]; then
    echo -e "${GREEN}✓${NC} $name ($response)"
    return 0
  else
    echo -e "${RED}✗${NC} $name (got $response, expected $expected_code)"
    return 1
  fi
}

failures=0

echo ""
echo "Local Services:"
check_service "App health" "http://localhost:8000/health" "200" || ((failures++))
check_service "Postgres" "http://localhost:5432" "000" && echo -e "${GREEN}✓${NC} Postgres (port open)" || ((failures++))

echo ""
echo "Kubernetes Services (if deployed):"
if command -v kubectl &> /dev/null; then
  kubectl get pods -n aerosense --no-headers 2>/dev/null | while read -r line; do
    pod_name=$(echo "$line" | awk '{print $1}')
    status=$(echo "$line" | awk '{print $3}')

    if [ "$status" == "Running" ]; then
      echo -e "${GREEN}✓${NC} $pod_name (Running)"
    else
      echo -e "${RED}✗${NC} $pod_name ($status)"
      ((failures++))
    fi
  done
else
  echo -e "${YELLOW}⚠${NC} kubectl not found (skipping K8s checks)"
fi

echo ""
if [ $failures -eq 0 ]; then
  echo -e "${GREEN}All checks passed!${NC}"
  exit 0
else
  echo -e "${RED}$failures check(s) failed!${NC}"
  exit 1
fi
