#!/bin/bash
# Example HITL workflow requests

BASE_URL="http://localhost:8000"

echo "=== HITL Approval Workflow Examples ==="

# 1. List pending actions
echo "1. Get pending HITL actions:"
curl -s "$BASE_URL/mcp/hitl/pending" | jq .

# 2. Submit an action for approval
echo ""
echo "2. Submit action for HITL approval:"
curl -s -X POST "$BASE_URL/mcp/hitl/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "action_id": "heal-locator-001",
    "action_type": "locator_healing",
    "proposed_change": {"selector": "input.email", "healing": "input[type=\"email\"]"},
    "confidence": 0.82,
    "reversible": true
  }' | jq .

# 3. Approve the action
echo ""
echo "3. Approve action:"
curl -s -X POST "$BASE_URL/mcp/hitl/approve/heal-locator-001" \
  -H "Content-Type: application/json" \
  -d '{"human_reviewer": "qa-engineer"}' | jq .

# 4. Deny an action
echo ""
echo "4. Deny action (alternative):"
curl -s -X POST "$BASE_URL/mcp/hitl/deny/heal-locator-001" \
  -H "Content-Type: application/json" \
  -d '{
    "human_reviewer": "qa-engineer",
    "reason": "Locator too specific, may break on CSS changes"
  }' | jq .

# 5. View audit trail
echo ""
echo "5. View audit log:"
curl -s "$BASE_URL/mcp/audit" | jq '.records[:3]'

# 6. Export audit log as CSV
echo ""
echo "6. Export audit log (CSV):"
curl -s "$BASE_URL/mcp/audit/export?format=csv" | head -5
