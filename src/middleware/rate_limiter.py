"""
Rate limiting middleware (Phase 5).
Enforces per-endpoint rate limits to prevent API exhaustion.
"""
from datetime import datetime, timedelta, timezone
from typing import Dict


class RateLimiter:
    """Simple in-memory rate limiter with per-endpoint configuration."""

    def __init__(self):
        self.limits: Dict[str, dict] = {
            "/mcp/generate_tests": {"requests": 10, "window": 60},  # 10 req/min
            "/mcp/hitl/submit": {"requests": 30, "window": 60},  # 30 req/min
            "/mcp/hitl/approve": {"requests": 50, "window": 60},  # 50 req/min
            "/mcp/audit": {"requests": 100, "window": 60},  # 100 req/min
        }
        self.requests: Dict[str, list] = {}

    def is_allowed(self, endpoint: str, client_id: str = "default") -> bool:
        """Check if request is allowed under rate limit.

        Args:
            endpoint: API endpoint path
            client_id: Client identifier (IP, API key, etc.)

        Returns:
            True if allowed, False if rate limited
        """
        if endpoint not in self.limits:
            return True  # No limit configured

        key = f"{endpoint}:{client_id}"
        now = datetime.now(timezone.utc)

        if key not in self.requests:
            self.requests[key] = []

        # Remove old requests outside window
        window_start = now - timedelta(seconds=self.limits[endpoint]["window"])
        self.requests[key] = [t for t in self.requests[key] if t > window_start]

        # Check if limit exceeded
        if len(self.requests[key]) >= self.limits[endpoint]["requests"]:
            return False

        # Record this request
        self.requests[key].append(now)
        return True

    def set_limit(self, endpoint: str, requests: int, window: int):
        """Configure rate limit for an endpoint.

        Args:
            endpoint: API endpoint path
            requests: Max requests in window
            window: Time window in seconds
        """
        self.limits[endpoint] = {"requests": requests, "window": window}


# Global rate limiter instance
_rate_limiter = RateLimiter()


def get_rate_limiter() -> RateLimiter:
    """Get global rate limiter instance."""
    return _rate_limiter
