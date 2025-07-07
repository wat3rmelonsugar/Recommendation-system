import smtplib
import os
from email.message import EmailMessage
from celery_config import app

# Загружаем конфигурацию из переменных окружения
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")  # Или другой SMTP-сервер
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))  # Обычно 587 для TLS
SMTP_USER = os.getenv("SMTP_USER", "*****")  # Ваш email
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "picv bcxh xyqn sssf")
PDF_FOLDER = "generated_pdfs"  # Папка, где хранятся PDF-файлы


@app.task
def send_email(pdf_path, recipient):
    """Отправляет email с прикрепленным PDF-файлом."""
    msg = EmailMessage()
    msg["Subject"] = "Ваши рекомендации по уходу за кожей"
    msg["From"] = SMTP_USER
    msg["To"] = recipient

    with open(pdf_path, "rb") as f:
        msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename=os.path.basename(pdf_path))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        return f"Email отправлен: {recipient}"
    except Exception as e:
        return f"Ошибка при отправке: {e}"


@app.task
def send_all_pdfs():
    """Находит все PDF-файлы и отправляет их пользователям."""
    if not os.path.exists(PDF_FOLDER):
        return "Папка с PDF не найдена"

    pdf_files = [f for f in os.listdir(PDF_FOLDER) if f.endswith(".pdf")]

    if not pdf_files:
        return "Нет PDF-файлов для отправки"

    results = []
    for pdf in pdf_files:
        user_email = get_email_from_filename(pdf)  # Получаем email из имени файла
        pdf_path = os.path.join(PDF_FOLDER, pdf)

        result = send_email(pdf_path, user_email)
        results.append(result)

        os.remove(pdf_path)  # Удаляем PDF после отправки

    return results


def get_email_from_filename(pdf_filename):
    """Извлекает email пользователя из имени файла (например, 'user@example.com.pdf')."""
    return pdf_filename.replace(".pdf", "").replace("_", "@")