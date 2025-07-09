# report_generator.py
import pandas as pd
import os
import logging
from datetime import datetime
from cache import cache

async def generate_report(df: pd.DataFrame, city: str) -> tuple[str, str]:
    """Генерация отчёта и CSV."""
    total_found = len(df)
    errors = len(df[df['error'].notnull() & (df['error'] == 'да')])
    total_members = df['members_count'].sum()
    
    report = f"""
⏳ Поиск по слову "{city}" завершён...

🔍 Найдено: {total_found} групп
🧹 После фильтрации: {total_found - errors}

✅ Результаты:
📁 В документе: {total_found - errors} группы
❗ Ошибок: {errors}
👥 Подписчиков суммарно: {total_members:,}
📊 Запросов к базе: 1
⬇️ Файл с результатами прикреплён ниже.
    """

    output_df = df[['name', 'link', 'members_count', 'views_count', 'er', 'geo', 'activity']].copy()
    output_df.columns = ['Название', 'Ссылка', 'Участников', 'Просмотры', 'ER', 'География', 'Живость']
    
    os.makedirs('results', exist_ok=True)
    file_name = f"results_{city}_{datetime.now().strftime('%Y%m%d')}.csv"
    file_path = f"results/{file_name}"
    
    output_df.to_csv(file_path, index=False, encoding='utf-8')
    file_size = os.path.getsize(file_path) / (1024 * 1024)
    if file_size > 5:
        logging.error(f"Файл {file_path} превышает 5 МБ")
        raise ValueError("Файл слишком большой (>5 МБ)")

    cache.set(f"file:{city.lower()}", {
        'file_path': file_path,
        'timestamp': datetime.now().isoformat()
    })
    
    logging.info(f"Сгенерирован файл: {file_path}")
    return report, file_path
