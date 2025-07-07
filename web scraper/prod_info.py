import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

# Настройки Chrome
options = Options()
options.add_argument("--ignore-certificate-errors")
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

# Функция для получения данных
def get_data(product_link, driver):
    # Создаем новый словарь для каждой ссылки
    data_dic = {'product': None, 'vendor': None, 'category': None,
                'price': None, 'ranking': None, 'skin_type': None}

    try:
        # Загружаем страницу
        driver.get(product_link)
        time.sleep(5)  # Добавляем ожидание для загрузки страницы

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # Извлечение данных
        data_dic['product'] = product_link.split('/')[4].strip()

        # Получаем производителя
        try:
            vendor_item = soup.find('div', class_='product__vendor')
            if vendor_item:
                vendor_link = vendor_item.find('a')
                if vendor_link:
                    vendor = vendor_link.text.strip()
                    data_dic['vendor'] = vendor
        except Exception as e:
            print(f"Error extracting vendor: {e}")

        # Получаем категорию
        try:
            info_items = soup.find_all('div', class_='productView-info-item')
            for item in info_items:
                name = item.find('span', class_='productView-info-name')
                value = item.find('span', class_='productView-info-value')
                if name and value and 'Product Type:' in name.text:
                    category = value.text.strip()
                    data_dic['category'] = category
        except Exception as e:
            print(f"Error extracting category: {e}")

        # Цена
        try:
            subtotal_span = soup.find('div', class_='productView-subtotal').find('span', class_='money')
            if subtotal_span:
                price_text = subtotal_span.text.strip()
                price = re.sub(r'[^\d.,]', '', price_text)
                data_dic['price'] = price
        except Exception as e:
            print(f"Error extracting price: {e}")

        # Рейтинг товара
        try:
            review_widget = soup.find('div', class_='jdgm-rev-widg')
            if review_widget:
                ranking = review_widget.get('data-average-rating')
                data_dic['ranking'] = ranking
        except Exception as e:
            print(f"Error extracting ranking: {e}")

        # Тип кожи
        try:
            match = re.search(r'Recommended for:\s*(.*)', soup.get_text())
            if match:
                recommended_for = match.group(1).strip()
                data_dic['skin_type'] = recommended_for
        except Exception as e:
            print(f"Error extracting 'Recommended for': {e}")

    except Exception as e:
        print(f"Error processing {product_link}: {e}")

    return data_dic

# Читаем файл со ссылками
input_file = 'data/product_links_updated.csv'
output_file = 'data/products_info.csv'

links_df = pd.read_csv(input_file)
product_links = links_df['product_links'].tolist()

# Инициализируем Selenium WebDriver
driver = webdriver.Chrome(options=options)

# Список для хранения всех данных
all_data = []

# Обрабатываем каждую ссылку
for link in product_links:
    print(f"Processing: {link}")
    data = get_data(link, driver)
    print(data)
    all_data.append(data)  # Добавляем копию данных в список

# Закрываем драйвер
driver.quit()

# Создаем DataFrame из собранных данных и сохраняем в CSV
output_df = pd.DataFrame(all_data)
output_df.to_csv(output_file, index=False)

print(f"Data successfully saved to {output_file}")


