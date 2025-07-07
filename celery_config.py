from celery import Celery

app = Celery('skincare_app',
             broker='redis://localhost:6379/0',
             backend='redis://localhost:6379/0',
             include=['recommendation', 'product_selection', 'pdf_generator', 'emailer'])
app.conf.update(
    result_expires=3600,
)
