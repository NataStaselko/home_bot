import asyncio
from aiogram import Router
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.bot import DefaultBotProperties
from core.config import settings
from routers import main_router
from core.filters import IsNotCommand
import redis.asyncio as redis


REDIS_URL = "redis://localhost:6379"
CHAT_ID = 1111111  # ID чата получателя
CHANNEL_1 = "message_channel"
CHANNEL_2 = "chat_channel"

async def start_redis_listener(bot: Bot, redis_url: str, channel: list):
    """
    Слушает Redis-канал и отправляет сообщения в чат при получении новых данных.
    """
    redis_client = await redis.from_url(redis_url, decode_responses=True)
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(*channel)
    async for redis_message in pubsub.listen():
        if redis_message['type'] == 'message':
            data = redis_message.get('data')
            if data:
                if redis_message['channel'] == CHANNEL_1:
                    await bot.send_message(CHAT_ID, f"Новое сообщение: {data}")
                else:
                    await bot.send_message(CHAT_ID, f"Чат отправителя: {data}")
            else:
                print("Получено пустое сообщение")

async def main():
    bot_properties = DefaultBotProperties(parse_mode=ParseMode.HTML)
    bot = Bot(token=settings.bot.token, default=bot_properties)
    dp = Dispatcher()
    dp.include_router(main_router)

    redis_listener_task = asyncio.create_task(
        start_redis_listener(bot, REDIS_URL, [CHANNEL_1, CHANNEL_2])
    ) # создается задача слушателя Redis-канала

    try:
        await dp.start_polling(bot)
    finally:
        redis_listener_task.cancel()  # Останавливаем задачу при завершении бота
        await redis_listener_task

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Interrupted by user")
