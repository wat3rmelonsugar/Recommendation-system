from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import requests

# Открываем файл и читаем его содержимое
with open('data/page_source.html', 'r', encoding='utf-8') as file:
    html_content = file.read()

# Передаём содержимое файла в BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Scraping brand links and save them into a list
brand_links = []
main_box = soup.find('div', class_='haloAZWrapper active-all')

if main_box:
    for brand in main_box.find_all('div'):
        brand_by_letter = brand.find('ul')
        if brand_by_letter:
            for links in brand_by_letter.find_all('li'):
                brand_link = links.find('a')  # Ищем тег <a>
                if brand_link:
                    href = brand_link.attrs.get('href', '')  # Получаем атрибут href
                    if href:
                        full_link = "https://koreanskincare.nl/" + href
                        brand_links.append(full_link)



# Write brand links into a file:
with open('data/brand_link.txt', 'w') as f:
    for item in brand_links:
        f.write(f"{item}\n")

# Indicate scraping completion
print(f'Got All Brand Links! There are {len(brand_links)} brands in total.')