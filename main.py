# main.py
import asyncio
import logging
import os
from aiogram import Dispatcher
from handlers import router
from middleware import RateLimitMiddleware, ErrorMiddleware
from bot_manager import BotManager
from database import init_db, load_groups_from_csv
from config import BOT_TOKEN

# Настройка логирования
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    filename='logs/bot.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def main():
    # Инициализация базы
    init_db()
    if os.path.exists('groups.csv'):
        load_groups_from_csv('groups.csv')
        logging.info("Данные из groups.csv загружены в SQLite")
    else:
        logging.error("groups.csv не найден")

    # Инициализация бота
    bot_manager = BotManager([BOT_TOKEN])
    dp = Dispatcher()
    dp.include_router(router)  # Регистрация router
    dp.message.middleware(RateLimitMiddleware())
    dp.message.middleware(ErrorMiddleware(bot_manager))
    
    logging.info("Бот запущен")
    await dp.start_polling(bot_manager.get_current_bot())

if __name__ == "__main__":
    asyncio.run(main())
