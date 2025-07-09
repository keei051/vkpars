# search_engine.py
import pandas as pd
import logging
from database import get_groups, get_banlist
from cache import cache
from datetime import datetime
import pymorphy2  # Для лемматизации

# Инициализация морфологического анализатора
morph = pymorphy2.MorphAnalyzer()

async def search_groups(city: str) -> pd.DataFrame:
    """Поиск и фильтрация групп по нормализованному названию города."""
    # Нормализация города (приведение к базовой форме)
    normalized_city = morph.parse(city)[0].normal_form

    cache_key = f"search:{normalized_city.lower()}"
    
    cached = cache.get(cache_key)
    if cached:
        logging.info(f"Данные для '{normalized_city}' из кэша")
        return pd.read_json(cached['dataframe'], orient='records')

    # Поиск в SQLite с учётом вариаций
    df = get_groups(normalized_city)
    if df.empty:
        logging.info(f"Группы для '{normalized_city}' не найдены")
        # Попробуем поиск с вариациями (например, Москва -> в Москве)
        df = get_groups_with_variations(normalized_city)
    
    if df.empty:
        logging.info(f"Группы для '{normalized_city}' и его вариаций не найдены")
        return df

    # Фильтрация по стоп-словам
    banlist = get_banlist()
    for word in banlist:
        df = df[~df['name'].str.contains(word, case=False,
