"""
Модуль с сервисами: поиск, кешбэк, инвесткопилка.
"""
import logging
import pandas as pd
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def simple_search(query: str, transactions: pd.DataFrame) -> List[Dict[str, Any]]:
    """Поиск транзакций по подстроке в описании или категории."""
    if not query or not isinstance(query, str):
        return []

    query_lower = query.lower().strip()
    if not query_lower:
        return []

    if "Описание" not in transactions.columns or "Категория" not in transactions.columns:
        logger.warning("Не хватает колонок 'Описание' или 'Категория' для поиска")
        return []

    mask_desc = transactions["Описание"].astype(str).str.contains(
        query_lower, case=False, na=False
    )
    mask_cat = transactions["Категория"].astype(str).str.contains(
        query_lower, case=False, na=False
    )

    result = transactions[mask_desc | mask_cat].copy()

    if "Дата операции" in result.columns:
        result["Дата операции"] = pd.to_datetime(
            result["Дата операции"], errors="coerce"
        ).dt.strftime("%d.%m.%Y")

    return result.to_dict(orient="records")


def search_by_phone(transactions: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Поиск транзакций с телефонными номерами в описании.
    Поддерживает любые форматы: +7 (900) 000-00-00, 8-900-000-00-00, 89000000000 и т.д.
    """
    if "Описание" not in transactions.columns:
        logger.warning("Колонка 'Описание' не найдена для поиска телефонов")
        return []

    phone_pattern = r'(?:\+7|8)\D*\d{3}\D*\d{3}\D*\d{2}\D*\d{2}'

    mask = transactions["Описание"].astype(str).str.contains(
        phone_pattern, regex=True, na=False
    )

    result = transactions[mask].copy()
    if "Дата операции" in result.columns:
        result["Дата операции"] = pd.to_datetime(
            result["Дата операции"], errors="coerce"
        ).dt.strftime("%d.%m.%Y")

    logger.info(f" Найдено {len(result)} транзакций с телефонными номерами")
    return result.to_dict(orient="records")


def search_transfers_to_individuals(transactions: pd.DataFrame) -> List[Dict[str, Any]]:
    """Поиск переводов физическим лицам."""
    if "Категория" not in transactions.columns or "Описание" not in transactions.columns:
        return []

    mask_cat = transactions["Категория"] == "Переводы"
    name_pattern = r'^[А-ЯЁ][а-яё]+\s+[А-ЯЁ]\.$'

    mask_name = transactions["Описание"].astype(str).str.contains(
        name_pattern, regex=True, na=False
    )

    result = transactions[mask_cat & mask_name].copy()
    if "Дата операции" in result.columns:
        result["Дата операции"] = pd.to_datetime(
            result["Дата операции"], errors="coerce"
        ).dt.strftime("%d.%m.%Y")

    return result.to_dict(orient="records")


def analyze_cashback(data: pd.DataFrame, year: int, month: int) -> Dict[str, int]:
    """Анализ выгодности категорий повышенного кешбэка."""
    df = data.copy()
    if "Дата операции" in df.columns:
        df["Дата операции"] = pd.to_datetime(df["Дата операции"], errors="coerce")
        mask = (df["Дата операции"].dt.year == year) & (df["Дата операции"].dt.month == month)
        df = df[mask]

    if "Категория" not in df.columns or "Сумма платежа" not in df.columns:
        return {}

    expenses = df[df["Сумма платежа"] < 0].copy()
    expenses["abs_amount"] = expenses["Сумма платежа"].abs()

    result = {}
    for category, group in expenses.groupby("Категория"):
        total = group["abs_amount"].sum()
        potential = int(total * 0.05)
        if potential > 0:
            result[category] = potential

    sorted_result = dict(sorted(result.items(), key=lambda x: x[1], reverse=True))
    return sorted_result


def investment_bank(month: str, transactions: List[Dict[str, Any]], limit: int) -> float:
    """Расчет суммы для Инвесткопилки."""
    total_saved = 0.0

    for txn in transactions:
        date_str = txn.get("Дата операции", "")
        if not date_str.startswith(month):
            continue

        amount = txn.get("Сумма операции", 0)
        if amount >= 0:
            continue

        abs_amount = abs(amount)
        rounded = ((abs_amount // limit) + 1) * limit if abs_amount % limit != 0 else abs_amount
        saved = rounded - abs_amount

        total_saved += saved

    return round(total_saved, 2)
