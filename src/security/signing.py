"""
Request signing and verification (Phase 5).
HMAC-SHA256 signatures for audit trail integrity.
"""
import hashlib
import hmac
import json
from datetime import datetime, timezone


def sign_request(payload: dict, secret: str) -> dict:
    """Sign a request payload with HMAC-SHA256.

    Args:
        payload: Data to sign
        secret: Shared secret key

    Returns:
        Payload with signature and timestamp
    """
    timestamp = datetime.now(timezone.utc).isoformat()

    # Create canonical form: sorted JSON for deterministic signing
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))

    # Create signature: HMAC(secret, timestamp + data)
    message = f"{timestamp}:{canonical}".encode()
    signature = hmac.new(
        secret.encode(), message, hashlib.sha256
    ).hexdigest()

    return {
        "payload": payload,
        "timestamp": timestamp,
        "signature": signature,
    }


def verify_signature(signed_data: dict, secret: str, max_age_seconds: int = 300) -> bool:
    """Verify a signed request and check timestamp.

    Args:
        signed_data: Data with signature and timestamp
        secret: Shared secret key
        max_age_seconds: Max allowed age of request (replay protection)

    Returns:
        True if signature valid and not expired
    """
    timestamp_str = signed_data.get("timestamp")
    signature = signed_data.get("signature")
    payload = signed_data.get("payload")

    if not all([timestamp_str, signature, payload]):
        return False

    # Verify timestamp within acceptable window
    try:
        timestamp = datetime.fromisoformat(timestamp_str)
        now = datetime.now(timezone.utc)
        age = (now - timestamp.replace(tzinfo=timezone.utc)).total_seconds()

        if age < 0 or age > max_age_seconds:
            return False
    except (ValueError, TypeError):
        return False

    # Verify signature
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    message = f"{timestamp_str}:{canonical}".encode()
    expected = hmac.new(
        secret.encode(), message, hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(signature, expected)
