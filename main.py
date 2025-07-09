import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from handlers import router
from middleware import RateLimitMiddleware, ErrorMiddleware
from bot_manager import BotManager
from database import init_db, load_groups_from_csv
from config import BOT_TOKEN

# Настройка логов
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    filename='logs/bot.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def main():
    init_db()
    if os.path.exists('groups.csv'):
        load_groups_from_csv('groups.csv')
        logging.info("Загружены данные из CSV")
    else:
        logging.warning("groups.csv не найден")

    bot_manager = BotManager([BOT_TOKEN])
    bot = bot_manager.get_current_bot()
    if not bot:
        logging.critical("BotManager не вернул бота")
        return

    await bot.set_my_commands([
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="add_ban", description="Добавить стоп-слово"),
        BotCommand(command="remove_ban", description="Удалить стоп-слово"),
        BotCommand(command="list_ban", description="Показать стоп-слова"),
        BotCommand(command="stats", description="Показать статистику"),
        BotCommand(command="update_data", description="Обновить группы из VK"),
    ])

    dp = Dispatcher()
    dp.include_router(router)
    dp.message.middleware(RateLimitMiddleware())
    dp.message.middleware(ErrorMiddleware(bot_manager))

    logging.info("Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

if __name__ == "__main__":
    asyncio.run(main())
