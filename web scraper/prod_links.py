import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Настройки Chrome
options = Options()
options.add_argument("--ignore-certificate-errors")
options.add_argument("--headless")  # Для работы без отображения браузера
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")


# Функция для сбора ссылок на продукты
product_links = []
def scape_product(link, driver):

    try:
        driver.get(link)

        # Ожидаем загрузку элементов с нужным селектором
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[class="card-link"]'))
        )

        products = driver.find_elements(By.CSS_SELECTOR, '[class="card-link"]')
        for product in products:
            product_links.append(product.get_attribute('href'))
    except Exception as e:
        print(f"Error scraping {link}: {e}")
    return product_links


# Читаем ссылки брендов из файла
product_link_dic = {'brand': [], 'product_links': []}

# Инициализируем Selenium драйвер
driver = webdriver.Chrome(options=options)

# Обрабатываем все бренды из файла
with open("data/brand_link.txt", "r") as file:
    for idx, brand_link in enumerate(file):
        brand_name = brand_link.split('/')[5].strip()
        print(f"Processing {brand_name}: {brand_link.strip()}")

        product_link_list = scape_product(brand_link.strip(), driver)

        # Сохраняем ссылки в словарь
        product_link_dic['brand'] += [brand_name] * len(product_link_list)
        product_link_dic['product_links'] += product_link_list

# Закрываем драйвер
driver.quit()

# Сохраняем результаты в CSV файл
product_link_df = pd.DataFrame(product_link_dic)
product_link_df.to_csv('data/product_links.csv', index=False)

# Уведомляем о завершении
print(f'Got All product Links! There are {len(product_link_df)} products in total.')
