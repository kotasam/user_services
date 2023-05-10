import random, string, uuid, re
import pika, json
import logging
from common.configs.config import config as cfg

from common.events.subscrider.send_email_subscriber import send_email_async


def random_string_generator(N, otp_type="alphanumeric"):
    if otp_type == "alpha":
        data_type = string.ascii_uppercase
    elif otp_type == "numeric":
        data_type = string.digits
    else:
        data_type = string.ascii_uppercase + string.digits

    return "".join(random.SystemRandom().choice(data_type) for _ in range(N))


def get_variables(data, values, default_value=None):
    return [data.get(key, default_value) for key in values]


def send_mail(message, routing_key, exchange_name):
    # def send_mail(email, code, user="1", subject="Registration"):
    # send_email_async.delay(code, email, user, subject)
    try:
        credentials = pika.PlainCredentials(
            cfg.get("rabbit_mq", "USER_NAME"), cfg.get("rabbit_mq", "PASSWORD")
        )
        parameters = pika.ConnectionParameters(
            host=cfg.get("rabbit_mq", "HOST"),
            virtual_host=cfg.get("rabbit_mq", "VIRTUAL_HOST"),
            credentials=credentials,
            frame_max=int(cfg.get("rabbit_mq", "FRAME_MAX")),
            heartbeat=int(cfg.get("rabbit_mq", "HEART_BEAT")),
            connection_attempts=int(cfg.get("rabbit_mq", "CONNECTION_ATTEMPTS")),
        )
        conn = pika.BlockingConnection(parameters)
        logging.info(f"conn: {conn}")
        channel = conn.channel()
        channel.exchange_declare(exchange=exchange_name, exchange_type="topic")
        channel.basic_publish(
            exchange=exchange_name, routing_key=routing_key, body=json.dumps(message)
        )
        conn.close()
        return True
    except Exception as err:
        print("Exception --->", err)
        logging.error(f"clientServiceCallback exception: {err}", exc_info=True)
        return None


def is_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


def not_uuid(val):
    try:
        uuid.UUID(str(val))
        return False
    except ValueError:
        return True


def check_mail(email):
    regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,10}\b"
    if re.fullmatch(regex, email):
        return True
    else:
        return False


def check_number(number):
    regex = r"\b[0-9+]{6,14}\b"
    if re.fullmatch(regex, number):
        return True
    else:
        return False
