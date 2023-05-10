import os
import httpx
import structlog
from structlog import get_logger

from common.configs.config import config as cfg

log = get_logger("Structured Logger")


# Custom processor
# Uses the New Relic Log API
# https://docs.newrelic.com/docs/logs/log-management/log-api/introduction-log-api/
def send_to_newrelic(logger, log_method, event_dict):

    # Your New Relic API Key
    # https://docs.newrelic.com/docs/apis/intro-apis/new-relic-api-keys/
    headers = {"Api-Key": cfg.get("newrelic", "API_KEY")}

    # Our log message and all the event context is sent as a JSON string
    # in the POST body
    # https://docs.newrelic.com/docs/logs/log-management/log-api/introduction-log-api/#json-content
    payload = {
        "message": f"{log_method} - {event_dict['event']}",
        "attributes": event_dict,
    }

    httpx.post("https://log-api.newrelic.com/log/v1", json=payload, headers=headers)

    return event_dict


# Configure Structlog's processor pipeline
structlog.configure(
    processors=[send_to_newrelic, structlog.processors.JSONRenderer()],
)
