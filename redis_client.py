# redis_client.py

import redis

redis_client = redis.Redis(
    host="127.0.0.1",   # force IPv4
    port=6379,
    db=0,               # 👈 EXPLICIT DB
    decode_responses=True
)


