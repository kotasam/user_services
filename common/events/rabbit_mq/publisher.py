import pika, json
from common.configs.config import config as cfg
import logging
from common.middlewares.newrelic_logs import get_logger


logger = get_logger()


def publish_event(message, exchange_name, routing_key):
    try:
        logging.error(f"message : {message}")
        logging.error(f"routing_key : {routing_key}")
        logging.error(f"exchange_name : {exchange_name}")
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
        logging.error(f"conn: {conn}")
        channel = conn.channel()
        logging.error(f"exchange declared")
        channel.exchange_declare(exchange=exchange_name, exchange_type="topic")
        logging.error(f"before publishing")
        channel.basic_publish(
            exchange=exchange_name, routing_key=routing_key, body=json.dumps(message)
        )
        conn.close()
        logging.error(f"event published and connection closed")
        logger.info(
            "EVENT SUCCESFULLY PUBLISHED TO "
            + exchange_name
            + "\n ROUTING KEY"
            + routing_key
            + "\n CURRENT PAYLOAD \n"
            + str(message)
        )
        return True
    except Exception as err:
        # logging.info(f"publish_event exception : {err}")
        logging.error(f"publish_event exception --->: {err}")
        # print("Exception --->", err)
        return False
