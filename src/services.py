import pandas as pd
from typing import List, Dict, Any

"""
Модуль с сервисами (кешбэк, инвесткопилка, поиск).
"""

def simple_search(query: str, transactions: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Поиск транзакций по подстроке в описании или категории.
    Регистронезависимый поиск.
    """
    if query is None or not isinstance(query, str):
        return []

    query_lower = query.lower().strip()
    if not query_lower:
        return []

    # Создаём маску для поиска
    mask_desc = transactions["Описание"].astype(str).str.contains(
        query_lower, case=False, na=False
    )
    mask_cat = transactions["Категория"].astype(str).str.contains(
        query_lower, case=False, na=False
    )

    # Фильтруем и конвертируем в список словарей
    result = transactions[mask_desc | mask_cat].copy()

    # Форматируем дату, если есть колонка
    if "Дата операции" in result.columns:
        result["Дата операции"] = pd.to_datetime(
            result["Дата операции"], errors="coerce"
        ).dt.strftime("%d.%m.%Y")

    return result.to_dict(orient="records")
