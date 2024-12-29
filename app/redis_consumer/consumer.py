from aiogram import Bot
from redis_consumer.base import RedisConsumerBase
from redis_consumer.schemas import MessageAddSchema
from core.config import settings


CHAT_ID = 845061443

class MessageConsumer(RedisConsumerBase):


    def __init__(self, bot: Bot):
        super().__init__(
            settings.redis.message_links.stream,
            settings.redis.message_links.group,
            settings.redis.message_links.consumer,
            settings.redis.url,
            settings.redis.message_links.maxlen,
        )
        self.bot = bot

    async def action(self, data: dict) -> bool:
        message_data = MessageAddSchema(**data)
        if message_data:
            await self.bot.send_message(CHAT_ID, f"Новое сообщение: {message_data.message_id}, Текст: {message_data.text}")
            return True
        return False
