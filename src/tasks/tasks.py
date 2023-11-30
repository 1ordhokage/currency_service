import smtplib

from email.message import EmailMessage

from celery import Celery

from src.tasks.config import smtp_settings
from src.utils.config import redis_settings


celery = Celery(
    "tasks",
    broker=redis_settings.connection_string
)


@celery.task
def send_welcome_email(user_email: str):
    email = EmailMessage()
    email["Subject"] = "Рады вас приветствовать!"
    email["From"] = smtp_settings.USER
    email["To"] = f"{user_email}"

    email.set_content(
        "<div>"
        "<h1>Здравствуйте. Спасибо за регистрацию!🤩</h1>"
        "</div>",
        subtype="html"
    )
    with smtplib.SMTP_SSL(smtp_settings.HOST, smtp_settings.PORT) as server:
        server.login(smtp_settings.USER, smtp_settings.PASSWORD)
        server.send_message(email)
