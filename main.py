from celery import chain
from recommendation import collect_user_answers, calculate_skin_type
from product_selection import select_products
from pdf_generator import generate_pdf
from emailer import send_email

def main():
    # Сбор ответов (синхронно)
    answers = collect_user_answers()

    # Создаем цепочку задач
    task_chain = chain(
        calculate_skin_type.s(answers) |  # Анализ ответов
        select_products.s() |            # Подбор продуктов
        generate_pdf.s()
    )

    # Запуск цепочки задач
    result = task_chain.apply_async()

    # Ожидание результата и вывод в консоль
    print("Обработка завершена. Результат:")
    pdf_filename = result.get()  # Получаем имя файла из Celery
    print(f"PDF-файл сохранен: {pdf_filename}")

if __name__ == "__main__":
    main()