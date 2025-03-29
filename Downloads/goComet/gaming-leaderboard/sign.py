import hmac
import hashlib
import time
import json

SECRET_KEY = "super-secret-key"  # Must match your server's secret key

# Build payload with current timestamp.
payload_dict = {
    "user_id": 1,
    "score": 500,
    "game_mode": "solo",
    "timestamp": int(time.time())
}

# Produce a compact JSON string.
payload = json.dumps(payload_dict, separators=(',', ':'))
signature = hmac.new(SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()

print("Payload:", payload)
print("Computed HMAC signature:", signature)