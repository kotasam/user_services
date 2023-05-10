from celery_server import app
from django.core.mail import EmailMultiAlternatives

from common.configs.config import config as cfg


@app.task(queue=cfg.get("celery", "QUEUE"))
def send_email_async(content, email, user, subject="email"):
    msg = EmailMultiAlternatives(
        subject + " : " + user, "", "support@worke.app", [email]
    )
    msg.attach_alternative(content, "text/html")
    msg.send()
