from celery_config import app
from fpdf import FPDF
import re

PDF_FOLDER = "generated_pdfs"

@app.task
def generate_pdf(recommendation_text, user_email):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=16)

    # Добавляем заголовок
    pdf.cell(200, 10, txt="Рекомендации по уходу за кожей", ln=True, align='C')

    # Добавляем текст рекомендаций
    pdf.multi_cell(0, 10, txt=recommendation_text)

    # Формируем имя файла на основе email (заменяем спецсимволы)
    safe_email = re.sub(r'[^a-zA-Z0-9]', '_', user_email)  # Заменяем запрещённые символы
    filename = f"{PDF_FOLDER}/{safe_email}.pdf"

    # Сохраняем PDF-файл
    pdf.output(filename)

    return filename
