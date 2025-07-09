# search_engine.py
import pandas as pd
import logging
from database import get_groups, get_banlist
from cache import cache
from datetime import datetime

async def search_groups(city: str) -> pd.DataFrame:
    """Поиск и фильтрация групп по городу."""
    cache_key = f"search:{city.lower()}"
    
    cached = cache.get(cache_key)
    if cached:
        logging.info(f"Данные для '{city}' из кэша")
        return pd.read_json(cached['dataframe'], orient='records')

    df = get_groups(city)
    if df.empty:
        logging.info(f"Группы для '{city}' не найдены")
        return df

    banlist = get_banlist()
    for word in banlist:
        df = df[~df['name'].str.contains(word, case=False, na=False)]

    cache.set(cache_key, {
        'dataframe': df.to_json(orient='records'),
        'timestamp': datetime.now().isoformat()
    })
    logging.info(f"Найдено {len(df)} групп для '{city}'")
    return df
