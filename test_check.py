import pandas as pd
from src.reports import spending_by_category

# Тестовые данные
data = {
    "Дата операции": ["2026-05-01", "2026-04-15", "2026-03-10", "2026-01-05"],
    "Категория": ["Супермаркеты", "Супермаркеты", "Кафе", "Супермаркеты"],
    "Сумма": [1200, 500, 300, 800]
}
df = pd.DataFrame(data)

# Вызываем функцию (декоратор сам сохранит JSON)
result = spending_by_category(df, "Супермаркеты")
print("✅ Функция отработала")
print(f"Найдено строк: {len(result)}")
print("📁 Файл spending_by_category_report.json должен появиться в корне проекта!")
