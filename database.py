# database.py
import sqlite3
import pandas as pd
import logging
from pathlib import Path

def init_db():
    """Инициализация SQLite базы."""
    conn = sqlite3.connect('vk_groups.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS groups (
            link TEXT,
            name TEXT,
            members_count INTEGER,
            views_count INTEGER,
            er REAL,
            geo TEXT,
            activity TEXT,
            error TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS banlist (
            word TEXT PRIMARY KEY
        )
    ''')
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_name ON groups (name)')
    conn.commit()
    return conn

def load_groups_from_csv(csv_path: str):
    """Загрузка групп из CSV."""
    if not Path(csv_path).exists():
        logging.error(f"Файл {csv_path} не найден")
        return
    conn = init_db()
    df = pd.read_csv(csv_path)
    df.to_sql('groups', conn, if_exists='replace', index=False)
    logging.info(f"Загружено {len(df)} строк из {csv_path}")
    conn.close()

def save_groups_from_vk(data: list):
    """Сохранение групп из VK API."""
    conn = init_db()
    cursor = conn.cursor()
    for item in data:
        cursor.execute('''
            INSERT OR REPLACE INTO groups (link, name, members_count, views_count, er, geo, activity, error)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            item.get('link', ''),
            item.get('name', ''),
            item.get('members_count', 0),
            item.get('views_count', 0),
            item.get('er', 0.0),
            item.get('geo', ''),
            item.get('activity', ''),
            item.get('error', '')
        ))
    conn.commit()
    conn.close()
    logging.info(f"Сохранено {len(data)} групп из VK API")

def get_groups(city: str) -> pd.DataFrame:
    """Поиск групп по городу."""
    conn = init_db()
    query = """
        SELECT * FROM groups 
        WHERE name LIKE ? 
        AND members_count >= 3000 
        AND (error IS NULL OR error != 'да')
    """
    df = pd.read_sql_query(query, conn, params=[f'%{city}%'])
    conn.close()
    return df

def get_banlist() -> list:
    """Получение стоп-слов."""
    conn = init_db()
    cursor = conn.cursor()
    cursor.execute("SELECT word FROM banlist")
    banlist = [row[0] for row in cursor.fetchall()]
    conn.close()
    return banlist

def add_ban_word(word: str):
    """Добавление стоп-слова."""
    conn = init_db()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO banlist (word) VALUES (?)", (word.lower(),))
    conn.commit()
    conn.close()
    logging.info(f"Добавлено стоп-слово: {word}")

def remove_ban_word(word: str):
    """Удаление стоп-слова."""
    conn = init_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM banlist WHERE word = ?", (word.lower(),))
    conn.commit()
    conn.close()
    logging.info(f"Удалено стоп-слово: {word}")
