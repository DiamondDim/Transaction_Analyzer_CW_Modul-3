import pandas as pd
from src.services import simple_search


def test_simple_search_basic():
    df = pd.DataFrame({
        "Описание": ["Магазин Пятёрочка", "Кафе Яндекс.Еда", "АЗС Лукойл"],
        "Категория": ["Супермаркеты", "Фастфуд", "Топливо"],
        "Сумма платежа": [500, 300, 2000]
    })

    result = simple_search("пятёрочка", df)
    assert len(result) == 1
    assert result[0]["Описание"] == "Магазин Пятёрочка"

    # Проверка регистра
    result2 = simple_search("ЯНДЕКС", df)
    assert len(result2) == 1
    assert "Яндекс.Еда" in result2[0]["Описание"]


def test_search_by_phone():
    """Проверка поиска транзакций с телефонными номерами."""
    df = pd.DataFrame({
        "Описание": [
            "Оплата МТС +7 (921) 111-22-33",
            "Звонок: 8-900-555-66-77",
            "Покупка в магазине",
            "Тинькофф Мобайл +79951234567",
            "Перевод Сергею",
        ],
        "Категория": ["Связь", "Связь", "Магазины", "Связь", "Переводы"],
        "Сумма платежа": [-100, -200, -500, -150, -1000],
        "Дата операции": ["2021-12-01"] * 5
    })

    from src.services import search_by_phone
    result = search_by_phone(df)

    # Должны найтись 3 транзакции с телефонами
    assert len(result) == 3

    # Проверка, что найдены нужные описания
    found = [r["Описание"] for r in result]
    assert any("МТС" in d for d in found)
    assert any("8-900-555-66-77" in d for d in found)
    assert any("Тинькофф" in d for d in found)

    # Проверка формата даты
    assert all(len(r["Дата операции"]) == 10 for r in result if r["Дата операции"])
