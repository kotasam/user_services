import pytz
from datetime import datetime
from common.configs.config import config as cfg


def getDeletedTime():
    # In future get timezone from Company settings
    time_zone = pytz.timezone(cfg.get("common", "TIME_ZONE"))
    return datetime.now(time_zone)


def getSerializerError(errors):
    if "non_field_errors" in errors:
        for error in errors["non_field_errors"]:
            return error
    if "organisation" in errors:
        return "Organisation is mandatory"
    if "created_by" in errors:
        return "Created by is mandatory"
    return "Something went wrong"
