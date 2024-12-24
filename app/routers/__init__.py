from aiogram import Router
from handlers.messages import router as messages_router

main_router = Router()

main_router.include_router(messages_router)
