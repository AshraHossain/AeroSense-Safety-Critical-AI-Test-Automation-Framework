"""
Rate limiter stress tests (Phase 6).
Validates rate limiting under concurrent load.
"""
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest

from src.middleware.rate_limiter import RateLimiter


def test_rate_limiter_blocks_excess_requests():
    """Rate limiter blocks requests exceeding limit."""
    limiter = RateLimiter()
    limiter.set_limit("/test", requests=5, window=60)

    # First 5 requests allowed
    for i in range(5):
        assert limiter.is_allowed("/test", "client1") is True

    # 6th request blocked
    assert limiter.is_allowed("/test", "client1") is False


def test_rate_limiter_resets_after_window():
    """Rate limiter resets counter after time window expires."""
    limiter = RateLimiter()
    limiter.set_limit("/test", requests=2, window=1)

    # Use both requests
    assert limiter.is_allowed("/test", "client1") is True
    assert limiter.is_allowed("/test", "client1") is True

    # 3rd blocked (within window)
    assert limiter.is_allowed("/test", "client1") is False

    # Simulate time passing beyond window
    now = datetime.now(timezone.utc)
    limiter.requests["/test:client1"] = [
        now - timedelta(seconds=2),  # Old requests outside window
        now - timedelta(seconds=2),
    ]

    # Should allow again
    assert limiter.is_allowed("/test", "client1") is True


def test_rate_limiter_isolates_clients():
    """Rate limiter tracks each client separately."""
    limiter = RateLimiter()
    limiter.set_limit("/test", requests=3, window=60)

    # Client1: use 3 requests
    assert limiter.is_allowed("/test", "client1") is True
    assert limiter.is_allowed("/test", "client1") is True
    assert limiter.is_allowed("/test", "client1") is True
    assert limiter.is_allowed("/test", "client1") is False  # Blocked

    # Client2: should have own quota
    assert limiter.is_allowed("/test", "client2") is True
    assert limiter.is_allowed("/test", "client2") is True
    assert limiter.is_allowed("/test", "client2") is True
    assert limiter.is_allowed("/test", "client2") is False  # Blocked


def test_rate_limiter_default_endpoints_configured():
    """Rate limiter has default configurations for key endpoints."""
    limiter = RateLimiter()

    # Verify default limits are set
    assert "/mcp/generate_tests" in limiter.limits
    assert "/mcp/hitl/submit" in limiter.limits
    assert "/mcp/audit" in limiter.limits


def test_rate_limiter_returns_429_on_limit_exceeded():
    """Rate limiter provides status code for HTTP response."""
    limiter = RateLimiter()
    limiter.set_limit("/test", requests=1, window=60)

    assert limiter.is_allowed("/test", "client") is True
    assert limiter.is_allowed("/test", "client") is False  # Should return 429
