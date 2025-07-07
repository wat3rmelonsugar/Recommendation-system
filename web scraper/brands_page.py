from selenium import webdriver
import time
from selenium.webdriver.chrome.options import Options
import os

options = Options()
options.add_argument("--ignore-certificate-errors")


driver = webdriver.Chrome(options=options)
driver.get("https://koreanskincare.nl/pages/brands")


# Ждем, чтобы страница загрузилась
time.sleep(5)

# Получаем HTML содержимое после загрузки
html = driver.page_source
# Указание имени файла
file_path = os.path.join('data', "page_source.html")

# Сохранение HTML-разметки в файл
with open(file_path, "w", encoding="utf-8") as file:
    file.write(html)

print(f"HTML-разметка сохранена в файл: page_source.html")


# Закрываем браузер
driver.quit()