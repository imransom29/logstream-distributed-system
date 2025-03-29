import time
import hmac
import hashlib
import os
from slowapi import Limiter
from slowapi.util import get_remote_address

# Use a secret key (make sure it’s the same everywhere)
SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key")

# Rate limiter: Limit to 10 requests per second per IP.
limiter = Limiter(key_func=get_remote_address)

def generate_signature(payload: str) -> str:
    """Compute the HMAC-SHA256 signature for the given payload."""
    return hmac.new(SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()

def verify_signature(payload: str, signature: str) -> bool:
    """Verify the signature matches the payload."""
    computed = generate_signature(payload)
    return hmac.compare_digest(computed, signature)

def is_replay(timestamp: float, max_age_seconds=30) -> bool:
    """Check if the request timestamp is older than allowed (anti-replay)."""
    return (time.time() - timestamp) > max_age_seconds