# config.py
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
VK_TOKEN = os.getenv('VK_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID'))  # Конвертация в int
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))

if not BOT_TOKEN or not VK_TOKEN or not ADMIN_ID:
    raise ValueError("BOT_TOKEN, VK_TOKEN и ADMIN_ID должны быть указаны в .env")
