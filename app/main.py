import asyncio
from typing import List
from aiogram import Router
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.bot import DefaultBotProperties
from core.config import settings
from routers import main_router
from core.filters import IsNotCommand
from redis_consumer.consumer import MessageConsumer


def get_bot():
    bot_properties = DefaultBotProperties(parse_mode=ParseMode.HTML)
    bot = Bot(token=settings.bot.token, default=bot_properties)
    return bot


async def start_consumers(consumers: List[MessageConsumer]):
    for consumer in consumers:
        await consumer.connect()
        asyncio.create_task(consumer.consume())


async def main():
    bot = get_bot()
    dp = Dispatcher()
    dp.include_router(main_router)

    message_consumer = MessageConsumer(bot=bot)
    await start_consumers([message_consumer])

    try:
        await dp.start_polling(bot)
    finally:
        await message_consumer.disconnect()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, RuntimeError):
        print("Interrupted by user")

