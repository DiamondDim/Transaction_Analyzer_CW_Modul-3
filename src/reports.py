import pandas as pd
import json
import logging
from functools import wraps
from typing import Optional, Callable, Any
from datetime import datetime

logger = logging.getLogger(__name__)

"""
Модуль для формирования отчетов.
"""

def save_report(filename: Optional[str] = None):
    """
    Декоратор: сохраняет результат функции в JSON-файл.

    Без параметра: использует имя по умолчанию.
    С параметром: использует переданное имя файла.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            print(f"🔥 DEBUG: Декоратор вызван! Функция: {func.__name__}")
            print(f"🔥 DEBUG: Аргументы: args={args}, kwargs={kwargs}")

            # Вызываем исходную функцию
            result = func(*args, **kwargs)

            # Определяем имя файла
            report_name = filename or f"report_{func.__name__}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            # Конвертируем DataFrame в JSON (если результат — DataFrame)
            if isinstance(result, pd.DataFrame):
                json_data = result.to_dict(orient="records")
            else:
                json_data = result

            # Сохраняем в файл
            try:
                with open(report_name, "w", encoding="utf-8") as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=2)
                logger.info(f"Отчёт сохранён: {report_name}")
                print(f"✅ DEBUG: Файл сохранён!")
            except Exception as e:
                logger.error(f"Ошибка сохранения отчёта: {e}")
                print(f"❌ DEBUG: Ошибка: {e}")

            return result

        return wrapper

    return decorator


@save_report(filename="spending_by_category_report.json")
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """
    Возвращает траты по заданной категории за последние три месяца.
    """


def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """
    Возвращает траты по задан категории за последние три месяца.
    """
    # 1. Определяем конечную дату
    end_date = pd.to_datetime(date) if date else pd.to_datetime("today")

    # 2. Считаем дату начала периода (3 месяца назад)
    start_date = end_date - pd.DateOffset(months=3)

    # 3. Фильтруем по категории (название колонки берём из ТЗ)
    cat_col = "Категория"
    if cat_col not in transactions.columns:
        raise ValueError(f"Колонка '{cat_col}' не найдена в датафрейме. Проверь заголовки Excel.")

    filtered = transactions[transactions[cat_col] == category].copy()

    # 4. Приводим даты к формату datetime
    date_col = "Дата операции"
    if date_col not in filtered.columns:
        raise ValueError(f"Колонка '{date_col}' не найдена в датафрейме.")

    filtered[date_col] = pd.to_datetime(filtered[date_col], errors="coerce")

    # 5. Оставляем только транзакции в диапазоне [start_date, end_date]
    mask = (filtered[date_col] >= start_date) & (filtered[date_col] <= end_date)
    result = filtered.loc[mask].copy()

    logger.info(
        f"Категория '{category}': найдено {len(result)} транзакций за период {start_date.date()} — {end_date.date()}")
    return result
