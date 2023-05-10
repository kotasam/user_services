import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.settings")
import django

django.setup()


import pika, json
from common.configs.config import config as cfg
import logging

from common.grpc.actions.crm_action import getContactInfo
from common.helpers.user_helper import createUser


def clientServiceCallback(ch, method, properties, body):
    try:
        print("In clientServiceCallback")
        json_body = json.loads(body)
        contact_info = getContactInfo(
            json_body["source_id"], json_body["department"], json_body["organisation"]
        )
        print("contact_info --->", contact_info)
        if not contact_info is None:
            user_creation_status = createUser(contact_info, json_body["client_id"])
            if not user_creation_status:
                # Handle the case
                pass
        else:
            # Handle the failed case
            pass
    except Exception as err:
        logging.error(f"clientServiceCallback exception: {err}", exc_info=True)
        pass


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
    channel.exchange_declare(
        exchange=cfg.get("events", "CLIENT_EXCHANGE"), exchange_type="topic"
    )

    result = channel.queue_declare(cfg.get("events", "CLIENT_QUEUE_NAME"), durable=True)
    queue_name = result.method.queue
    channel.queue_bind(
        exchange=cfg.get("events", "CLIENT_EXCHANGE"),
        queue=queue_name,
        routing_key=cfg.get("events", "CLIENT_CREATE_ROUTING_KEY"),
    )
except Exception as err:
    logging.error(f"Worke user service consumer exception: {err}", exc_info=True)
    pass


channel.basic_consume(
    queue=queue_name, on_message_callback=clientServiceCallback, auto_ack=True
)

print("Consumer started...")
channel.start_consuming()
