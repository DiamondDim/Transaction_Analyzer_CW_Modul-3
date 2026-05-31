# Transaction Analyzer — Курсовая работа (Модуль 3)

Приложение для анализа банковских транзакций из Excel-файла.

## ✅ Реализовано

### Веб-страницы
- [x] Страница «Главная»: приветствие, карты, топ-5 транзакций, курсы валют, цены акций

### Сервисы  
- [x] Простой поиск: регистронезависимый поиск по описанию и категории

### Отчёты
- [x] Траты по категории за 3 месяца
- [x] Декоратор `@save_report` для сохранения отчётов в JSON

## 🚀 Запуск

```bash
# Установка зависимостей
poetry install

# Запуск тестов
pytest -v

# Запуск приложения
python -m src.main
```

## 📁 Структура проекта

```
.
├── src/
│   ├── main.py      # Точка входа
│   ├── views.py     # Веб-страницы (JSON-генерация)
│   ├── services.py  # Сервисы (поиск, кешбэк, инвесткопилка)
│   ├── reports.py   # Отчёты с декоратором
│   └── utils.py     # Общие утилиты
├── tests/           # Юнит-тесты
├── data/
│   └── operations.xlsx  # Исходные данные
├── user_settings.json   # Настройки пользователя
└── pyproject.toml       # Зависимости Poetry
```

## 🧪 Тесты

### Все тесты проходят: 12 passed

```
======================================================================================================= test session starts =======================================================================================================
platform win32 -- Python 3.13.13, pytest-7.4.4, pluggy-1.6.0 -- C:\Users\###\AppData\Local\pypoetry\Cache\virtualenvs\transaction-analyzer-cw-modul-3-hRUQe7VC-py3.13\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\###\Desktop\Transaction_Analyzer_CW_Modul-3
plugins: cov-4.1.0
collected 12 items                                                                                                                                                                                                                 

tests/test_services.py::test_simple_search_basic PASSED                                                                                                                                                                      [  8%]
tests/test_utils.py::test_get_greeting_morning PASSED                                                                                                                                                                        [ 16%]
tests/test_utils.py::test_get_greeting_afternoon PASSED                                                                                                                                                                      [ 25%]
tests/test_utils.py::test_get_greeting_evening PASSED                                                                                                                                                                        [ 33%]
tests/test_utils.py::test_get_greeting_night PASSED                                                                                                                                                                          [ 41%]
tests/test_views.py::TestGetGreeting::test_all_intervals PASSED                                                                                                                                                              [ 50%]
tests/test_views.py::TestFilterTransactions::test_filters_by_month PASSED                                                                                                                                                    [ 58%]
tests/test_views.py::TestCardInfo::test_calculation PASSED                                                                                                                                                                   [ 66%]
tests/test_views.py::TestTopTransactions::test_sorted_by_abs_amount PASSED                                                                                                                                                   [ 75%]
tests/test_views.py::TestMain::test_structure_and_types PASSED                                                                                                                                                               [ 83%]
tests/test_views.py::TestMain::test_greetings_for_times PASSED                                                                                                                                                               [ 91%]
tests/test_views.py::TestSettings::test_load_user_settings_real PASSED                                                                                                                                                       [100%]

======================================================================================================= 12 passed in 1.24s ========================================================================================================

```

