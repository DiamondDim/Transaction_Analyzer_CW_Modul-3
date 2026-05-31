import json
import requests
from datetime import datetime
from typing import Any
import pandas as pd
from pathlib import Path


def get_greeting(hour: int) -> str:
    if 6 <= hour < 12: return "Доброе утро"
    if 12 <= hour < 18: return "Добрый день"
    if 18 <= hour < 23: return "Добрый вечер"
    return "Доброй ночи"


def load_user_settings() -> dict:
    settings_path = Path(__file__).parent.parent / "user_settings.json"
    with open(settings_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_currency_rates(currencies: list[str]) -> list[dict]:
    rates = []
    try:
        resp = requests.get("https://www.cbr-xml-daily.ru/daily_json.js", timeout=5)
        resp.raise_for_status()
        data = resp.json()
        for curr in currencies:
            if curr in data["Valute"]:
                rates.append({"currency": curr, "rate": round(data["Valute"][curr]["Value"], 2)})
    except Exception:
        for curr in currencies:
            rates.append({"currency": curr, "rate": 0.0})
    return rates


def get_stock_prices(stocks: list[str]) -> list[dict]:
    prices = []
    try:
        for stock in stocks:
            resp = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{stock}", timeout=5)
            if resp.status_code == 200:
                price = resp.json()["chart"]["result"][0]["meta"]["regularMarketPrice"]
                prices.append({"stock": stock, "price": round(price, 2)})
    except Exception:
        for stock in stocks:
            prices.append({"stock": stock, "price": 0.0})
    return prices


def load_transactions(file_path: str | Path) -> pd.DataFrame:
    return pd.read_excel(file_path)


def filter_transactions_by_date(transactions: pd.DataFrame, date_str: str) -> pd.DataFrame:
    df = transactions.copy()
    if "Дата операции" not in df.columns:
        return df
        
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], errors="coerce")
    target = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    start_month = target.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    mask = (df["Дата операции"] >= start_month) & (df["Дата операции"] <= target)
    return df[mask]


def get_card_info(transactions: pd.DataFrame) -> list[dict]:
    cards = []
    if "Номер карты" in transactions.columns and "Сумма платежа" in transactions.columns:
        grouped = transactions.groupby("Номер карты")
        for card_num, group in grouped:
            expenses = group.loc[group["Сумма платежа"] < 0, "Сумма платежа"].abs().sum()
            cards.append({
                "last_digits": str(card_num),
                "total_spent": round(float(expenses), 2),
                "cashback": round(float(expenses) * 0.01, 2)
            })
    return cards


def get_top_transactions(transactions: pd.DataFrame, top_n: int = 5) -> list[dict]:
    top = []
    if "Сумма платежа" not in transactions.columns:
        return top
        
    df_sorted = transactions.reindex(
        transactions["Сумма платежа"].abs().sort_values(ascending=False).index
    ).head(top_n)
    
    for _, row in df_sorted.iterrows():
        date_val = row.get("Дата операции")
        if pd.isna(date_val):
            date_fmt = ""
        elif isinstance(date_val, datetime):
            date_fmt = date_val.strftime("%d.%m.%Y")
        else:
            try:
                date_fmt = pd.to_datetime(date_val).strftime("%d.%m.%Y")
            except Exception:
                date_fmt = str(date_val)
                
        top.append({
            "date": date_fmt,
            "amount": round(float(row["Сумма платежа"]), 2),
            "category": str(row.get("Категория", "")),
            "description": str(row.get("Описание", ""))
        })
    return top


def main(date_time: str, transactions: pd.DataFrame = None) -> dict[str, Any]:
    """
    Главная функция. 
    Если transactions=None, загружает из data/operations.xlsx.
    Для тестов можно передать готовый DataFrame напрямую.
    """
    if transactions is None:
        data_path = Path(__file__).parent.parent / "data" / "operations.xlsx"
        transactions = load_transactions(data_path)
        
    dt = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
    transactions = filter_transactions_by_date(transactions, date_time)
    
    settings = load_user_settings()
    
    return {
        "greeting": get_greeting(dt.hour),
        "cards": get_card_info(transactions),
        "top_transactions": get_top_transactions(transactions, top_n=5),
        "currency_rates": get_currency_rates(settings["user_currencies"]),
        "stock_prices": get_stock_prices(settings["user_stocks"])
    }
