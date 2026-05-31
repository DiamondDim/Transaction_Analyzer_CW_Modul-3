"""
Основной модуль приложения.
"""
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Точка входа в приложение."""
    logger.info("Приложение запущено")
    print("Добро пожаловать в систему анализа транзакций!")


if __name__ == "__main__":
    main()
