import asyncio
from redis.asyncio import Redis

async def test_redis():
    redis = Redis.from_url("redis://localhost:6379/0")
    await redis.set("test_key", "hello redis")
    value = await redis.get("test_key")
    print(value)  # Should print: b'hello redis'

asyncio.run(test_redis())
