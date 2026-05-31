"""
Модуль с сервисами: поиск, кешбэк, инвесткопилка.
"""
import logging
import re
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


def simple_search(query: str, transactions: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Поиск транзакций по подстроке в описании или категории.
    Регистронезависимый поиск.

    :param query: строка для поиска
    :param transactions: DataFrame с транзакциями
    :return: список словарей с найденными транзакциями
    """
    if not query or not isinstance(query, str):
        return []

    query_lower = query.lower().strip()
    if not query_lower:
        return []

    # Проверяем наличие нужных колонок
    if "Описание" not in transactions.columns or "Категория" not in transactions.columns:
        logger.warning("Не хватает колонок 'Описание' или 'Категория' для поиска")
        return []

    # Создаём маску для поиска (без учёта регистра)
    mask_desc = transactions["Описание"].astype(str).str.contains(
        query_lower, case=False, na=False
    )
    mask_cat = transactions["Категория"].astype(str).str.contains(
        query_lower, case=False, na=False
    )

    # Фильтруем
    result = transactions[mask_desc | mask_cat].copy()

    # Форматируем дату, если есть
    if "Дата операции" in result.columns:
        result["Дата операции"] = pd.to_datetime(
            result["Дата операции"], errors="coerce"
        ).dt.strftime("%d.%m.%Y")

    return result.to_dict(orient="records")


def search_by_phone(transactions: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Поиск транзакций с телефонными номерами в описании.
    Поддерживает форматы: +7 (900) 000-00-00, 89000000000, +79001234567
    """
    if "Описание" not in transactions.columns:
        return []

    # Regex для российских мобильных номеров
    phone_pattern = r'(\+7|8)\s*\(?9\d{2}\)?[\s\.-]?\d{3}[\s\.-]?\d{2}[\s\.-]?\d{2}'

    mask = transactions["Описание"].astype(str).str.contains(
        phone_pattern, regex=True, na=False
    )

    result = transactions[mask].copy()
    if "Дата операции" in result.columns:
        result["Дата операции"] = pd.to_datetime(
            result["Дата операции"], errors="coerce"
        ).dt.strftime("%d.%m.%Y")

    return result.to_dict(orient="records")


def search_transfers_to_individuals(transactions: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Поиск переводов физическим лицам.
    Критерии: категория "Переводы" + имя и первая буква фамилии с точкой (напр. "Валерий А.")
    """
    if "Категория" not in transactions.columns or "Описание" not in transactions.columns:
        return []

    # Фильтр по категории
    mask_cat = transactions["Категория"] == "Переводы"

    # Паттерн: Имя + пробел + Заглавная буква + точка
    # Например: "Валерий А.", "Сергей З."
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
    """
    Анализирует, сколько кешбэка можно было бы получить по каждой категории
    при выборе её в качестве категории повышенного кешбэка.

    :return: JSON {категория: потенциальный_кешбэк_в_рублях}
    """
    # Фильтруем по месяцу
    df = data.copy()
    if "Дата операции" in df.columns:
        df["Дата операции"] = pd.to_datetime(df["Дата операции"], errors="coerce")
        mask = (df["Дата операции"].dt.year == year) & (df["Дата операции"].dt.month == month)
        df = df[mask]

    if "Категория" not in df.columns or "Сумма платежа" not in df.columns:
        return {}

    # Считаем траты по категориям (только расходы)
    expenses = df[df["Сумма платежа"] < 0].copy()
    expenses["abs_amount"] = expenses["Сумма платежа"].abs()

    # Группируем и считаем потенциальный кешбэк (предположим 5% для повышенного)
    result = {}
    for category, group in expenses.groupby("Категория"):
        total = group["abs_amount"].sum()
        # 5% повышенного кешбэка (можно изменить под требования)
        potential = int(total * 0.05)
        if potential > 0:
            result[category] = potential

    # Сортируем по убыванию и берём топ
    sorted_result = dict(sorted(result.items(), key=lambda x: x[1], reverse=True))
    return sorted_result


def investment_bank(month: str, transactions: List[Dict[str, Any]], limit: int) -> float:
    """
    Рассчитывает сумму, которую можно отложить в «Инвесткопилку».

    :param month: месяц в формате 'YYYY-MM'
    :param transactions: список транзакций с полями 'Дата операции', 'Сумма операции'
    :param limit: шаг округления (10, 50, 100)
    :return: сумма к откладыванию
    """
    total_saved = 0.0

    for txn in transactions:
        # Проверяем дату
        date_str = txn.get("Дата операции", "")
        if not date_str.startswith(month):
            continue

        # Проверяем, что это расход
        amount = txn.get("Сумма операции", 0)
        if amount >= 0:  # только траты
            continue

        abs_amount = abs(amount)

        # Округляем вверх до ближайшего limit
        rounded = ((abs_amount // limit) + 1) * limit if abs_amount % limit != 0 else abs_amount
        saved = rounded - abs_amount

        total_saved += saved

    return round(total_saved, 2)
