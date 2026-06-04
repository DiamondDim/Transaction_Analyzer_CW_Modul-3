"""
Модуль для генерации JSON-ответов веб-страниц.
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import requests

from .utils import get_greeting

logger = logging.getLogger(__name__)


def load_user_settings() -> dict:
    """Загружает настройки пользователя из JSON."""
    settings_path = Path(__file__).parent.parent / "user_settings.json"
    with open(settings_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_currency_rates(currencies: List[str]) -> List[Dict[str, float]]:
    """
    Получает курсы валют с cbr-xml-daily.ru.
    Возвращает только валидные курсы (rate > 0).
    """
    rates = []
    try:
        resp = requests.get("https://www.cbr-xml-daily.ru/daily_json.js", timeout=5)
        resp.raise_for_status()
        data = resp.json()

        for curr in currencies:
            curr_data = data.get("Valute", {}).get(curr)
            if curr_data and curr_data.get("Value", 0) > 0:
                rates.append({
                    "currency": curr,
                    "rate": round(curr_data["Value"], 2)
                })
            else:
                logger.warning(f"Курс для {curr} не найден или <= 0, пропускаем.")
    except requests.RequestException as e:
        logger.error(f"Ошибка при запросе курсов валют: {e}")
    except Exception as e:
        logger.error(f"Непредвиденная ошибка при получении курсов: {e}")

    return rates


def get_stock_prices(stocks: List[str]) -> List[Dict[str, float]]:
    """
    Получает цены акций с Yahoo Finance.
    Возвращает только валидные цены (price > 0).
    """
    prices = []
    base_url = "https://query1.finance.yahoo.com/v8/finance/chart"

    for stock in stocks:
        try:
            resp = requests.get(f"{base_url}/{stock}", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                result = data.get("chart", {}).get("result", [])
                if result and result[0].get("meta", {}).get("regularMarketPrice"):
                    price = result[0]["meta"]["regularMarketPrice"]
                    if price > 0:
                        prices.append({"stock": stock, "price": round(float(price), 2)})
                    else:
                        logger.warning(f"Цена для {stock} <= 0, пропускаем.")
                else:
                    logger.warning(f"Не удалось извлечь цену для {stock} из ответа API.")
            else:
                logger.warning(f"HTTP {resp.status_code} для акции {stock}")
        except requests.RequestException as e:
            logger.warning(f"Ошибка сети при запросе {stock}: {e}")
        except (KeyError, ValueError, IndexError) as e:
            logger.warning(f"Ошибка парсинга ответа для {stock}: {e}")
        except Exception as e:
            logger.warning(f"Непредвиденная ошибка для {stock}: {e}")

    return prices


def load_transactions(file_path: str | Path) -> pd.DataFrame:
    """Загружает транзакции из Excel-файла."""
    return pd.read_excel(file_path)


def filter_transactions_by_date(transactions: pd.DataFrame, date_str: str) -> pd.DataFrame:
    """
    Фильтрует транзакции: от начала месяца до указанной даты (включительно).
    Работает как с реальными данными (строки), так и с тестовыми (datetime).
    """
    df = transactions.copy()

    if "Дата операции" not in df.columns:
        logger.warning("Колонка 'Дата операции' не найдена в данных")
        return df

    # Приводим колонку к datetime (без dayfirst — чтобы не ломать тесты с ISO-форматом)
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], errors="coerce")

    # Парсим целевую дату из строки формата "YYYY-MM-DD HH:MM:SS"
    target = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    start_month = target.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Создаём маску: дата >= начало месяца И дата <= целевая дата
    # Отбрасываем NaT (невалидные даты) через notna()
    mask = (
        df["Дата операции"].notna()
        & (df["Дата операции"] >= start_month)
        & (df["Дата операции"] <= target)
    )

    return df[mask].copy()


def get_card_info(transactions: pd.DataFrame) -> List[Dict[str, Any]]:
    """Собирает информацию по картам: последние 4 цифры, расходы, кешбэк."""
    cards = []
    if "Номер карты" not in transactions.columns or "Сумма платежа" not in transactions.columns:
        logger.warning("Не хватает колонок для расчёта информации по картам")
        return cards

    grouped = transactions.groupby("Номер карты")
    for card_num, group in grouped:
        # Считаем только расходы (отрицательные суммы)
        expenses = group.loc[group["Сумма платежа"] < 0, "Сумма платежа"].abs().sum()
        if expenses > 0:
            cards.append({
                "last_digits": str(card_num),
                "total_spent": round(float(expenses), 2),
                "cashback": round(float(expenses) * 0.01, 2)  # 1% кешбэк
            })
    return cards


def get_top_transactions(transactions: pd.DataFrame, top_n: int = 5) -> List[Dict[str, Any]]:
    """Возвращает топ-N транзакций по модулю суммы платежа."""
    if "Сумма платежа" not in transactions.columns:
        return []

    # Сортируем по абсолютному значению суммы
    df_sorted = transactions.reindex(
        transactions["Сумма платежа"].abs().sort_values(ascending=False).index
    ).head(top_n)

    result = []
    for _, row in df_sorted.iterrows():
        date_val = row.get("Дата операции")

        # Форматируем дату в dd.mm.yyyy
        if pd.isna(date_val):
            date_fmt = ""
        elif isinstance(date_val, datetime):
            date_fmt = date_val.strftime("%d.%m.%Y")
        else:
            try:
                date_fmt = pd.to_datetime(date_val).strftime("%d.%m.%Y")
            except Exception:
                date_fmt = str(date_val)

        result.append({
            "date": date_fmt,
            "amount": round(float(row["Сумма платежа"]), 2),
            "category": str(row.get("Категория", "")),
            "description": str(row.get("Описание", ""))
        })
    return result


def main(date_time: str, transactions: pd.DataFrame = None) -> Dict[str, Any]:
    """
    Главная функция страницы «Главная».

    :param date_time: строка в формате "YYYY-MM-DD HH:MM:SS"
    :param transactions: опционально готовый DataFrame (для тестов)
    :return: JSON-ответ со всеми данными для страницы
    """
    # Загружаем транзакции, если не переданы
    if transactions is None:
        data_path = Path(__file__).parent.parent / "data" / "operations.xlsx"
        transactions = load_transactions(data_path)

    # Парсим дату и фильтруем данные
    dt = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
    filtered = filter_transactions_by_date(transactions, date_time)

    # Загружаем настройки пользователя
    settings = load_user_settings()

    # Формируем ответ
    return {
        "greeting": get_greeting(dt.hour),
        "cards": get_card_info(filtered),
        "top_transactions": get_top_transactions(filtered, top_n=5),
        "currency_rates": get_currency_rates(settings.get("user_currencies", [])),
        "stock_prices": get_stock_prices(settings.get("user_stocks", []))
    }
