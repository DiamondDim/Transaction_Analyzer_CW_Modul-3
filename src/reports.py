"""
Модуль для формирования отчетов.
"""
import pandas as pd
import json
import logging
from functools import wraps
from typing import Optional, Callable, Any
from datetime import datetime

logger = logging.getLogger(__name__)


def save_report(filename: Optional[str] = None):
    """
    Декоратор: сохраняет результат функции в JSON-файл.

    Без параметра: использует имя по умолчанию.
    С параметром: использует переданное имя файла.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
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
            except Exception as e:
                logger.error(f"Ошибка сохранения отчёта: {e}")

            return result

        return wrapper

    return decorator

