import pytest
import pandas as pd
from datetime import datetime
from unittest.mock import patch, MagicMock
from src.views import (
    get_greeting,
    get_card_info,
    get_top_transactions,
    filter_transactions_by_date,
    main,
    load_user_settings
)


@pytest.fixture
def mock_df():
    return pd.DataFrame({
        "Дата операции": ["2021-12-01", "2021-12-15", "2021-12-20", "2021-11-30", "2021-12-20"],
        "Номер карты": ["5814", "5814", "7512", "5814", "7512"],
        "Сумма платежа": [-1000.0, -262.0, -15000.0, -400.0, 500.0],
        "Категория": ["Супермаркеты", "Супермаркеты", "Переводы", "Кафе", "Зарплата"],
        "Описание": ["Пятёрочка", "Магнит", "Иванов И.И.", "Кофе", "ООО Ромашка"]
    })


@pytest.fixture
def mock_requests():
    with patch("src.views.requests.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        # Имитируем ответ API
        mock_resp.json.return_value = {
            "Valute": {"USD": {"Value": 73.21}, "EUR": {"Value": 87.08}},
            "chart": {"result": [{"meta": {"regularMarketPrice": 150.12}}]}
        }
        mock_get.return_value = mock_resp
        yield mock_get


class TestGetGreeting:
    def test_all_intervals(self):
        assert get_greeting(6) == "Доброе утро"
        assert get_greeting(11) == "Доброе утро"
        assert get_greeting(12) == "Добрый день"
        assert get_greeting(17) == "Добрый день"
        assert get_greeting(18) == "Добрый вечер"
        assert get_greeting(22) == "Добрый вечер"
        assert get_greeting(23) == "Доброй ночи"
        assert get_greeting(5) == "Доброй ночи"


class TestFilterTransactions:
    def test_filters_by_month(self, mock_df):
        res = filter_transactions_by_date(mock_df, "2021-12-20 14:30:00")
        assert len(res) == 4  # Исключили одну запись за ноябрь
        assert "2021-11-30" not in res["Дата операции"].values


class TestCardInfo:
    def test_calculation(self, mock_df):
        # 1. Сначала фильтруем данные (как делает функция main)
        # Это исключит транзакцию за 30.11 (-400.0)
        filtered_df = filter_transactions_by_date(mock_df, "2021-12-20 14:30:00")

        # 2. Теперь считаем карточки
        res = get_card_info(filtered_df)

        assert len(res) == 2
        assert res[0]["last_digits"] == "5814"
        # Теперь сумма верная: 1000 + 262 = 1262
        assert res[0]["total_spent"] == 1262.0
        assert res[0]["cashback"] == 12.62


class TestTopTransactions:
    def test_sorted_by_abs_amount(self, mock_df):
        # Для топа транзакций тоже лучше фильтровать,
        # но в этом тесте проверяем сортировку на всем наборе
        res = get_top_transactions(mock_df, top_n=3)

        # Топ-1 по модулю: -15000 (Переводы)
        assert res[0]["amount"] == -15000.0
        assert res[0]["date"] == "20.12.2021"
        assert "category" in res[0] and "description" in res[0]


class TestMain:
    @patch("src.views.load_user_settings", return_value={"user_currencies": ["USD"], "user_stocks": ["AAPL"]})
    def test_structure_and_types(self, mock_settings, mock_df, mock_requests):
        res = main("2021-12-20 14:30:00", transactions=mock_df)

        assert res["greeting"] == "Добрый день"
        assert isinstance(res["cards"], list) and len(res["cards"]) == 2
        assert isinstance(res["top_transactions"], list) and len(res["top_transactions"]) <= 5
        assert isinstance(res["currency_rates"], list) and res["currency_rates"][0]["currency"] == "USD"
        assert isinstance(res["stock_prices"], list) and res["stock_prices"][0]["stock"] == "AAPL"

        for t in res["top_transactions"]:
            assert len(t["date"]) == 10 and t["date"][2] == "." and t["date"][5] == "."

    @patch("src.views.load_user_settings", return_value={"user_currencies": [], "user_stocks": []})
    def test_greetings_for_times(self, mock_settings, mock_df, mock_requests):
        times = [
            ("2021-12-20 08:00:00", "Доброе утро"),
            ("2021-12-20 14:00:00", "Добрый день"),
            ("2021-12-20 20:00:00", "Добрый вечер"),
            ("2021-12-20 02:00:00", "Доброй ночи")
        ]
        for dt, expected in times:
            assert main(dt, transactions=mock_df)["greeting"] == expected


class TestSettings:
    def test_load_user_settings_real(self):
        """Проверяет, что файл настроек читается и имеет правильную структуру."""
        settings = load_user_settings()  # Вызываем реальную функцию

        assert "user_currencies" in settings
        assert "user_stocks" in settings
        assert isinstance(settings["user_currencies"], list)
        assert isinstance(settings["user_stocks"], list)
        # Проверяем, что валюты — строки
        assert all(isinstance(c, str) for c in settings["user_currencies"])
