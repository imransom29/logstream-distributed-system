import requests
import random
import time
import json
import hmac
import hashlib

API_BASE_URL = "http://127.0.0.1:8000/api/leaderboard"
SECRET_KEY = "super-secret-key"  # Must match your server's secret key

def submit_score(user_id, score, game_mode, timestamp):
    payload_obj = {
        "user_id": user_id,
        "score": score,
        "game_mode": game_mode,
        "timestamp": timestamp
    }
    payload_str = json.dumps(payload_obj, separators=(',', ':'))
    signature = hmac.new(SECRET_KEY.encode(), payload_str.encode(), hashlib.sha256).hexdigest()
    headers = {
        "Content-Type": "application/json",
        "X-Signature": signature
    }
    response = requests.post(f"{API_BASE_URL}/submit", headers=headers, data=payload_str)
    return response

def get_top_players():
    response = requests.get(f"{API_BASE_URL}/top")
    return response.json()

def get_user_rank(user_id):
    response = requests.get(f"{API_BASE_URL}/rank/{user_id}")
    return response.json()

if __name__ == "__main__":
    while True:
        # Use valid user IDs; for example, if you pre-populated 100,000 users:
        user_id = random.randint(1, 100000)
        score = random.randint(100, 10000)
        game_mode = "solo"
        timestamp = int(time.time())
        res = submit_score(user_id, score, game_mode, timestamp)
        print("Submit:", res.status_code, res.json())
        print("Top 10:", get_top_players())
        print("Rank for user", user_id, ":", get_user_rank(user_id))
        time.sleep(random.uniform(0.5, 2))