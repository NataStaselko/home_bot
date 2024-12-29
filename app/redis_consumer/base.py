from typing import Any
from abc import ABC, abstractmethod

import asyncio

import redis.asyncio as redis
from redis.exceptions import ResponseError



class RedisClient:
    def __init__(self, redis_url="redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis = None

    async def connect(self):
        self.redis = redis.from_url(self.redis_url)

    async def disconnect(self):
        await self.redis.aclose()


class RedisStreamBase(RedisClient):
    def __init__(self, stream: str, redis_url="redis://localhost:6379", maxlen=1000):
        super().__init__(redis_url)
        self.maxlen = maxlen
        self.stream = stream

    async def count_messages(self):
        count = await self.redis.xlen(self.stream)
        return count

    async def trim_stream(self):
        # Calculate the timestamp for one week ago
        await self.redis.xtrim(self.stream, maxlen=self.maxlen, approximate=False)


class RedisConsumerBase(RedisStreamBase, ABC):
    def __init__(
        self,
        stream: str,
        group_name: str,
        consumer_name: str,
        redis_url="redis://localhost:6379",
        maxlen=1000,
    ):
        super().__init__(stream, redis_url, maxlen)
        self.group_name = group_name
        self.consumer_name = consumer_name

    async def _connect_group(self):
        try:
            await self.redis.xgroup_create(
                self.stream, self.group_name, id="0", mkstream=True
            )
        except ResponseError as e:
            if "BUSYGROUP Consumer Group name already exists" not in str(e):
                raise e

    async def read_history(self, stream, start="-", end="+", count=10):
        messages = await self.redis.xrange(stream, min=start, max=end, count=count)
        return messages

    @abstractmethod
    async def action(self, data) -> bool:
        """Define how to process a message."""
        pass

    async def consume(self):
        await self._connect_group()

        while True:
            try:
                messages = await self.redis.xreadgroup(
                    self.group_name, self.consumer_name, streams={self.stream: ">"}, count=1
                )
                for message in messages:
                    stream_name, message_list = message
                    for msg_id, data in message_list:
                        data = {
                            k.decode('utf-8'): v.decode('utf-8') for k, v in data.items()
                        }
                        is_ok = await self.action(data)
                        if is_ok:
                            await self.redis.xack(self.stream, self.group_name, msg_id)
                        else:
                            print(f"Error processing message {msg_id}: {data}")

            except Exception as e:
                print(f"Error consuming from {self.stream}: {e}")
            await asyncio.sleep(1.01)