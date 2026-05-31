"""
Тесты для модуля utils.
"""
from src.utils import get_greeting


def test_get_greeting_morning():
    assert get_greeting(8) == "Доброе утро"


def test_get_greeting_afternoon():
    assert get_greeting(14) == "Добрый день"


def test_get_greeting_evening():
    assert get_greeting(20) == "Добрый вечер"


def test_get_greeting_night():
    assert get_greeting(2) == "Доброй ночи"
