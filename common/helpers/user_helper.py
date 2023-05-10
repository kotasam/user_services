from users.models import User
from common.events.rabbit_mq.publisher import publish_event
from common.configs.config import config as cfg


def getUserPayload(user, client_id):
    return {
        "organisation": str(user.organisation),
        "client_id": str(client_id),
        "user_id": str(user.id),
    }


def createUser(data, client_id):
    try:
        user = User.objects.get(
            email=data["email"],
            organisation=data["organisation"],
            # phone_number=data["phone_number"],
        )
        user.fname = data["first_name"]
        user.lname = data["last_name"]
        user.phone_number = data["phone_number"]
        user.save()
        event_status = publish_event(
            getUserPayload(user, client_id),
            cfg.get("events", "USER_EXCHANGE"),
            cfg.get("events", "USER_CREATE_ROUTING_KEY"),
        )
        if not event_status:
            return False
        return True
    except Exception as err:
        print("First exception --->", err)
        pass

    try:
        user = User(
            fname=data["first_name"],
            lname=data["last_name"],
            email=data["email"],
            username=(
                data["email"].split("@")[0]
                + "--STAFF--"
                + data["organisation"]
                + "@"
                + data["email"].split("@")[1]
            ),
            utype=User.UserTypes.ENDUSER,
            phone_number=data["phone_number"],
            organisation=data["organisation"],
        )
        user.save()
        event_status = publish_event(
            getUserPayload(user, client_id),
            cfg.get("events", "USER_EXCHANGE"),
            cfg.get("events", "USER_CREATE_ROUTING_KEY"),
        )
        if not event_status:
            return False
        return True
    except Exception as err:
        print("Second exception --->", err)
        return False


def getAdminCreationPayload(organisation_id, role):
    return {"organisation": organisation_id, "role": role}
