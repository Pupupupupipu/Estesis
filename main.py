import os

from dotenv import load_dotenv
from fastapi import FastAPI
import uvicorn
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

from api.couriers import couriers_api
from api.orders import orders_api

app = FastAPI()
app.include_router(couriers_api)
app.include_router(orders_api)

load_dotenv()

@app.on_event("startup")
async def startup_event():
    redis = aioredis.from_url(f"redis://{os.environ.get('REDIS_HOST')}:{os.environ.get('REDIS_PORT')}", encoding="utf8", decode_response=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)