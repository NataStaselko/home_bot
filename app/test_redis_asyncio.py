import asyncio
import redis.asyncio as redis

async def main():
    redis_client = redis.Redis()
    pong = await redis_client.ping()
    print(f"Ping: {pong}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())