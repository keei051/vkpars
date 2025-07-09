# middleware.py
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
import asyncio
import logging
from collections import defaultdict
from datetime import datetime, timedelta

class RateLimitMiddleware(BaseMiddleware):
    """Ограничение 5 запросов в минуту."""
    def __init__(self):
        self.requests = defaultdict(list)
        self.limit = 5
        self.window = timedelta(minutes=1)

    async def __call__(self, handler, event: TelegramObject, data: dict):
        user_id = event.from_user.id
        now = datetime.now()
        
        self.requests[user_id] = [t for t in self.requests[user_id] if now - t < self.window]
        
        if len(self.requests[user_id]) >= self.limit:
            await event.answer("❗ Слишком много запросов. Подождите минуту.")
            return
        
        self.requests[user_id].append(now)
        return await handler(event, data)

class ErrorMiddleware(BaseMiddleware):
    """Обработка ошибок Telegram API."""
    def __init__(self, bot_manager):
        self.bot_manager = bot_manager

    async def __call__(self, handler, event: TelegramObject, data: dict):
        try:
            return await handler(event, data)
        except Exception as e:
            logging.error(f"Ошибка: {e}")
            if "429" in str(e):
                await asyncio.sleep(2)
                return await handler(event, data)
            bot = self.bot_manager.get_current_bot()
            await bot.send_message(
                event.chat.id,
                "❗ Произошла ошибка. Попробуйте позже."
            )
            from config import ADMIN_ID
            await bot.send_message(ADMIN_ID, f"⚠️ Ошибка: {e}")
            raise e
