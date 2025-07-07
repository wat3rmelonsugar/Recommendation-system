import pandas as pd
import numpy as np
from celery_config import app

## Соответствие типов кожи и их кодов
SKIN_TYPE_CODES = {
    "Oily": "O",
    "Dry": "D",
    "Normal": "N",
    "Combined": "C"
}

# Соответствие особенностей кожи и их кодов
CONDITION_CODES = {
    "acne": "A",
    "wrinkles": "Age",
    "irritated": "I",
    "pigm": "P",
    "sens": "S"
}

@app.task
def generate_recommendation_text(products):
    """Формирует текстовую рекомендацию на основе подобранных товаров"""
    text = "На основе вашего типа кожи мы рекомендуем следующие продукты:\n\n"
    for category, items in products.items():
        text += f"{category}:\n"
        for item in items:
            text += f"- {item['product']} (Цена: {item['price']} руб., Рейтинг: {item['ranking']})\n"
        text += "\n"
    return text

@app.task
def select_products(recommendations):
    """Фильтрует продукты по типу кожи и особенностям"""
    skin_type, conditions = recommendations  # Распаковываем кортеж

    # Загружаем CSV с товарами
    df = pd.read_csv("cleaned_file_with_codes.csv")

    # Код типа кожи (берем первый элемент списка)
    skin_code = SKIN_TYPE_CODES.get(skin_type[0], "") if skin_type else ""

    # Коды особенностей кожи
    condition_codes = {CONDITION_CODES[c] for c in conditions if c in CONDITION_CODES}

    # Фильтрация по типу кожи
    filtered_products = df[
        df['skin_type_code'].str.contains(skin_code, na=False)
    ]

    # Дополнительная фильтрация по рейтингу
    filtered_products = filtered_products[filtered_products['ranking'] >= 4.4]

    # Фильтрация по проблемам кожи (если есть)
    if condition_codes:
        filtered_products = filtered_products[
            filtered_products['skin_problem_code'].astype(str).apply(lambda x: any(c in x for c in condition_codes))
        ]

    selected_products = {}

    # Оставляем только нужные категории
    categories = ['Cleanser', 'Toner', 'Essence', 'Serum']

    for category in categories:
        cat_products = filtered_products[filtered_products['category'] == category]

        if cat_products.empty:  # Если нет товаров в этой категории, пропускаем
            continue

        # Создаём копию, чтобы избежать предупреждений
        cat_products = cat_products.copy()

        # Считаем медиану цен
        median_price = np.median(cat_products['price'])

        # Выбираем 3 товара, ближайшие к медианной цене
        cat_products.loc[:, 'Price_Diff'] = abs(cat_products['price'] - median_price)

        if cat_products.empty:  # Проверяем снова, если фильтрация убрала все товары
            continue

        best_matches = cat_products.nsmallest(3, 'Price_Diff')

        # Заполняем словарь рекомендаций
        selected_products[category] = best_matches[['product', 'price', 'ranking']].to_dict(orient='records')

    # Генерируем текст рекомендации
    recommendation_text = generate_recommendation_text(selected_products)

    return recommendation_text

