import asyncio
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from core.base_handler import Handler
import aiohttp
from core.filters import IsNotCommand

router = Router()

API_URL = "http://localhost:8000/v1/messages"


@router.message(Command("start"))
async def start_command(message: Message):
    await message.answer("Добро пожаловать! Чем я могу вам помочь?")


@router.message(Command("get_messages"))
async def get_message(message: Message):
    handler = Handler(method="GET", url=API_URL)
    try:
        result = await handler.request(response_type="json")
        await message.answer(f"Ваше сообщение: {result}")
    except Exception as e:
        await message.answer(f"Не удалось получить сообщение: {e}")


@router.message(IsNotCommand())
async def handle_message(message: Message):
    handler = Handler(
        method="POST",
        url=API_URL,
        data={
            'message_id': message.message_id,
            "from_user_id": message.from_user.id,
            "chat_id": message.chat.id,
            "text": message.text,
            "date": int(message.date.timestamp())
        }
    )
    try:
        result = await handler.request(response_type="json")
        await message.answer(f"Сообщение сохранено: {result}")
    except Exception as e:
        await message.answer(f"Не удалось сохранить сообщение: {e}")
