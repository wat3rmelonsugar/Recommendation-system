import pandas as pd
import string
import matplotlib.pyplot as plt
import seaborn as sns

# Замените 'your_file.csv' на путь к вашему файлу
file_path = 'data/products_info.csv'

# Чтение файла CSV
df = pd.read_csv(file_path)

# Функция для очистки строки от точек и кавычек
def clean_skin_type(value):
    if pd.isna(value) or value.strip() == "":
        return "All skin types"
    # Убираем только точки и кавычки
    return value.replace('"', '').replace("'", '').replace('.', '')

# Применение функции к столбцу skin_type
df['skin_type'] = df['skin_type'].apply(clean_skin_type)


# Функция для разделения строки на токены
def tokenize(value):
    # Разделяем строку по запятой и обрабатываем пробелы
    tokens = [token.strip() for token in value.split(",")]
    return tokens

# Применение функции tokenize к столбцам
all_tokens = set()

# Применяем токенизацию для каждого столбца (например, для 'skin_type')
for column in ['skin_type']:  # Можно добавить другие столбцы
    for value in df[column]:
        all_tokens.update(tokenize(value))

tokens_df = pd.DataFrame(sorted(all_tokens), columns=["Skin conditions"])

# Сохранение уникальных токенов в отдельный CSV файл
tokens_df.to_csv("data/unique_tokens.csv", index=False)

# Сохранение изменений обратно в CSV (если нужно)
df.to_csv("data/cleaned_file.csv", index=False)

# Проверяем результат
print(df.head())

# Преобразуем цену в числовой формат
df['price'] = pd.to_numeric(df['price'], errors='coerce')

# Для каждой категории находим продукты с высоким рейтингом
threshold_rating = df['ranking'].mean()  # Средний рейтинг
df['high_rating'] = df['ranking'] >= threshold_rating  # Отметка товаров с высоким рейтингом

# Рассчитываем среднюю цену для продуктов с высоким рейтингом
df_high_rating = df[df['high_rating']].copy()

# Группировка по категориям и брендам, затем находим бренд с максимальным количеством товаров с высоким рейтингом
top_brands = df_high_rating.groupby(['category', 'vendor']).size().reset_index(name='product_count')

# Для каждой категории выбираем бренд с максимальным количеством продуктов
top_brands = top_brands.loc[top_brands.groupby('category')['product_count'].idxmax()]

# Рассчитываем среднюю цену для выбранных брендов
top_brands_with_avg_price = top_brands.merge(df_high_rating, on=['category', 'vendor'], how='left')

# Для каждого бренда в категории находим среднюю цену
top_brands_with_avg_price = top_brands_with_avg_price.groupby('category').agg(
    average_price=('price', 'mean'), top_brand=('vendor', 'first')).reset_index()

# Построение графика
plt.figure(figsize=(14, 8))
sns.barplot(x='category', y='average_price', data=top_brands_with_avg_price, hue='category', dodge=False)

# Добавляем названия брендов на график
for i, row in top_brands_with_avg_price.iterrows():
    plt.text(x=i,
             y=row['average_price'] + 0.5,  # Располагаем немного выше столбца
             s=row['top_brand'],
             ha='center',
             va='bottom',
             fontsize=9,
             rotation=90)

# Настроим график
plt.title("Top Brand in Each Category with the Highest Number of High-Rating Products and Their Average Price")
plt.xlabel("Product Categories")
plt.ylabel("Average Price")
plt.xticks(rotation=90)  # Поворот меток по оси X для удобства чтения
plt.legend(title='Category', loc='upper right')

# Показать график
plt.tight_layout()
plt.show()