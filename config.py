import os
from dotenv import load_dotenv

# Загружаем .env
load_dotenv()

# Получаем переменные
BOT_TOKEN = os.getenv('BOT_TOKEN')
VK_TOKEN = os.getenv('VK_TOKEN')
ADMIN_ID_RAW = os.getenv('ADMIN_ID')
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))

# Проверяем, что всё есть
required_vars = {
    "BOT_TOKEN": BOT_TOKEN,
    "VK_TOKEN": VK_TOKEN,
    "ADMIN_ID": ADMIN_ID_RAW
}
missing = [k for k, v in required_vars.items() if not v]

if missing:
    raise ValueError(f"❌ Отсутствуют обязательные переменные в .env: {', '.join(missing)}")

# Преобразуем ADMIN_ID в int после проверки
ADMIN_ID = int(ADMIN_ID_RAW)

