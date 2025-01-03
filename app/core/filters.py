from aiogram.filters import BaseFilter
from aiogram.types import Message


class IsNotCommand(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return not message.text.startswith("/")