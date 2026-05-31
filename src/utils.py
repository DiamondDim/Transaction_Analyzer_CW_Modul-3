"""
Модуль с общими утилитами.
"""
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


def get_greeting(hour: Optional[int] = None) -> str:
    """Возвращает приветствие в зависимости от времени суток."""
    if hour is None:
        hour = datetime.now().hour

    if 6 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"
