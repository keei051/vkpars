import os

BOT_TOKEN = os.getenv('BOT_TOKEN')
VK_TOKEN = os.getenv('VK_TOKEN')
ADMIN_ID_RAW = os.getenv('ADMIN_ID')
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))

required_vars = {
    "BOT_TOKEN": BOT_TOKEN,
    "VK_TOKEN": VK_TOKEN,
    "ADMIN_ID": ADMIN_ID_RAW
}
missing = [k for k, v in required_vars.items() if not v]

if missing:
    raise ValueError(f"❌ Отсутствуют обязательные переменные окружения: {', '.join(missing)}")

ADMIN_ID = int(ADMIN_ID_RAW)
