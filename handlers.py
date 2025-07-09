from aiogram import Router, F, types
from aiogram.filters import Command
from bot_manager import BotManager
from search_engine import search_groups
from report_generator import generate_report
from database import add_ban_word, remove_ban_word, get_banlist, save_groups_from_vk
from config import ADMIN_ID, VK_TOKEN
import logging
import os
import requests
import re

router = Router()

@router.message(Command(commands=['start']))
async def start_command(message: types.Message):
    await message.answer("👁️‍🗨️ Я бот для поиска сообществ ВКонтакте!\n"
                         "Используйте: поиск(Город), например, поиск(Ижевск)")
    logging.info(f"Команда /start от {message.from_user.id}")

@router.message(F.text.startswith("поиск("))
async def search_command(message: types.Message):
    match = re.fullmatch(r"поиск\(([\w\sА-Яа-яёЁ\-]+)\)", message.text.strip())
    if not match:
        await message.answer("❗ Некорректный формат. Используйте: поиск(Город)")
        return

    city = match.group(1).strip()
    bot = BotManager([os.getenv('BOT_TOKEN')]).get_current_bot()
    await bot.send_message(message.chat.id, f"⏳ Начинаю поиск по слову '{city}'...")
    logging.info(f"Поиск: '{city}' от {message.from_user.id}")

    try:
        df = await search_groups(city)
        if df.empty:
            await bot.send_message(message.chat.id,
                f"❌ Ничего не найдено по запросу '{city}'.\n"
                "Попробуйте другое слово или проверьте орфографию.")
            return

        report, file_path = await generate_report(df, city)
        await bot.send_message(message.chat.id, report)

        with open(file_path, 'rb') as file:
            await bot.send_document(message.chat.id, file, caption=f"⬇️ Результаты для '{city}'")
        
        logging.info(f"Успешно отправлен результат для '{city}' пользователю {message.from_user.id}")

    except Exception as e:
        logging.error(f"Ошибка при поиске '{city}': {e}")
        await bot.send_message(message.chat.id, "❗ Произошла ошибка. Попробуйте позже.")

# --- Остальные команды без изменений (они написаны корректно) ---

@router.message(Command(commands=['add_ban']))
async def add_ban_command(message: types.Message):
    if message.from_user.id != int(ADMIN_ID):
        await message.answer("❌ Доступ запрещён.")
        return
    word = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
    if not word:
        await message.answer("❗ Укажите слово: /add_ban магазин")
        return
    add_ban_word(word.lower())
    await message.answer(f"✅ Слово '{word}' добавлено в стоп-лист.")

@router.message(Command(commands=['remove_ban']))
async def remove_ban_command(message: types.Message):
    if message.from_user.id != int(ADMIN_ID):
        await message.answer("❌ Доступ запрещён.")
        return
    word = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
    if not word:
        await message.answer("❗ Укажите слово: /remove_ban магазин")
        return
    remove_ban_word(word.lower())
    await message.answer(f"✅ Слово '{word}' удалено из стоп-листа.")

@router.message(Command(commands=['list_ban']))
async def list_ban_command(message: types.Message):
    if message.from_user.id != int(ADMIN_ID):
        await message.answer("❌ Доступ запрещён.")
        return
    banlist = get_banlist()
    if banlist:
        await message.answer("📜 Стоп-слова:\n" + "\n".join(banlist))
    else:
        await message.answer("📜 Стоп-лист пуст.")

@router.message(Command(commands=['stats']))
async def stats_command(message: types.Message):
    if message.from_user.id != int(ADMIN_ID):
        await message.answer("❌ Доступ запрещён.")
        return
    await message.answer("📊 Статистика (заглушка):\n- Запросов: 0\n- Уникальных городов: 0")

@router.message(Command(commands=['update_data']))
async def update_data_command(message: types.Message):
    if message.from_user.id != int(ADMIN_ID):
        await message.answer("❌ Доступ запрещён.")
        return
    bot = BotManager([os.getenv('BOT_TOKEN')]).get_current_bot()
    await bot.send_message(message.chat.id, "⏳ Начинаю обновление данных из VK API...")
    logging.info(f"Обновление данных от {message.from_user.id}")

    try:
        url = "https://api.vk.com/method/groups.search"
        params = {
            "access_token": VK_TOKEN,
            "q": "",
            "count": 1000,
            "v": "5.131"
        }
        response = requests.get(url, params=params)
        data = response.json()

        if "error" in data:
            await bot.send_message(message.chat.id, f"❗ Ошибка VK API: {data['error']['error_msg']}")
            logging.error(f"VK API ошибка: {data['error']['error_msg']}")
            return

        groups = []
        for group in data.get("response", {}).get("items", []):
            groups.append({
                "link": f"https://vk.com/club{group['id']}",
                "name": group.get("name", ""),
                "members_count": group.get("members_count", 0),
                "views_count": 0,
                "er": 0.0,
                "geo": "",
                "activity": "Живая" if group.get("is_closed", 0) == 0 else "Закрытая",
                "error": ""
            })

        save_groups_from_vk(groups)
        await bot.send_message(message.chat.id, f"✅ Обновлено {len(groups)} групп из VK API.")
        logging.info(f"Обновлено {len(groups)} групп")

    except Exception as e:
        logging.error(f"Ошибка при обновлении данных: {e}")
        await bot.send_message(message.chat.id, "❗ Ошибка при обновлении данных. Проверь логи.")
