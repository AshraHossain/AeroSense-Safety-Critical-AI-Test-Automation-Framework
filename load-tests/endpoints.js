import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '30s', target: 20 },   // Ramp-up: 0 to 20 users over 30s
    { duration: '1m30s', target: 20 }, // Sustained: 20 users for 90s
    { duration: '30s', target: 40 },   // Spike: 20 to 40 users over 30s
    { duration: '1m', target: 40 },    // Sustained: 40 users for 60s
    { duration: '30s', target: 0 },    // Ramp-down: 40 to 0 users over 30s
  ],
  thresholds: {
    'http_req_duration': ['p(95)<500', 'p(99)<1000'], // 95th percentile < 500ms
    'http_req_failed': ['rate<0.1'],                   // Error rate < 10%
  },
};

export default function () {
  // Test /mcp/generate_tests endpoint
  let generateRes = http.post(
    'http://localhost:8000/mcp/generate_tests',
    JSON.stringify({
      srs_content: 'REQ-001: Test endpoint\nREQ-002: Validate input',
      confidence_threshold: 0.75,
      auto_run: false,
    }),
    { headers: { 'Content-Type': 'application/json' } }
  );

  check(generateRes, {
    'POST /mcp/generate_tests status is 201': (r) => r.status === 201,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });

  // Test /mcp/hitl/pending endpoint
  let pendingRes = http.get('http://localhost:8000/mcp/hitl/pending');
  check(pendingRes, {
    'GET /mcp/hitl/pending status is 200': (r) => r.status === 200,
  });

  // Test /mcp/audit endpoint
  let auditRes = http.get('http://localhost:8000/mcp/audit');
  check(auditRes, {
    'GET /mcp/audit status is 200': (r) => r.status === 200,
  });

  sleep(1);
}
