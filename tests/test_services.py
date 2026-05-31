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
