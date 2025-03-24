import os

import redis
from flask_caching import Cache
from dotenv import load_dotenv

load_dotenv()

cache = Cache(config={
    "CACHE_TYPE": os.environ.get("CACHE_TYPE"),
    "CACHE_REDIS_URL": os.getenv("REDIS_URL"),
    "CACHE_DEFAULT_TIMEOUT": int(os.getenv("CACHE_TIMEOUT", 21600))
})
redis_client = redis.StrictRedis.from_url(
    os.getenv("REDIS_URL"), decode_responses=True
)