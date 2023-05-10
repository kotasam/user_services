import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.settings")
import django

django.setup()

import grpc
from concurrent import futures
from common.configs.config import config as cfg
from common.grpc.protopys import user_service_pb2_grpc
from common.grpc.protopys import user_service_pb2
from common.grpc.services.user_services import UserServices
from organisation.models import Organisations, Locations
from users.models import User
import logging
from common.middlewares.newrelic_logs import get_logger

logger = get_logger()


class UserServicesServicer(user_service_pb2_grpc.UserServicesServicer):
    def GetOrganisation(self, request, context):
        id = request.id
        organisation_data_reply = user_service_pb2.OrganisationData()
        try:
            organisation = Organisations.objects.get(
                status=True,
                is_active=True,
                id=id,
            )
            logger.info(f"organisation ---->{organisation}")
            organisation_data_reply.valid = True
            organisation_data_reply.id = str(organisation.id)
            organisation_data_reply.slug = str(organisation.slug)
            organisation_data_reply.name = str(organisation.name)
            organisation_data_reply.description = str(organisation.description)
            organisation_data_reply.email = str(organisation.email)
            organisation_data_reply.phone_number = str(organisation.phone_number)
            organisation_data_reply.ccode = str(organisation.ccode)
            organisation_data_reply.image = str(organisation.image)
            organisation_data_reply.website = str(organisation.website)
            organisation_data_reply.address = str(organisation.address)
            organisation_data_reply.identifier = str(organisation.identifier)
            organisation_data_reply.registration_id = str(organisation.registration_id)
            logger.info(f"organisation_data_reply ---->{organisation_data_reply}")
            return organisation_data_reply
        except Exception as err:
            logging.error(f"GetOrganisation service Exception: {err}", exc_info=True)
            organisation_data_reply.valid = False
            return organisation_data_reply.valid

    def GetUserData(self, request, context):
        id = request.id
        logger.info(f"id ---->{id}")
        user_data_reply = user_service_pb2.UserData()
        try:
            user = User.objects.get(
                status=True,
                is_active=True,
                id=id,
            )
            logger.info(f"user ---->{user}")
            user_data_reply.valid = True
            user_data_reply.id = str(user.id)
            user_data_reply.fname = str(user.fname)
            user_data_reply.lname = str(user.lname)
            user_data_reply.username = str(user.username)
            user_data_reply.email = str(user.email)
            user_data_reply.phone_number = str(user.phone_number)
            user_data_reply.ccode = str(user.ccode)
            user_data_reply.image = str(user.image)
            user_data_reply.utype = str(user.utype)
            user_data_reply.status = user.status
            user_data_reply.organisation = str(user.organisation)
            logger.info(f"user_data_reply ---->{user_data_reply}")
            return user_data_reply
        except Exception as err:
            logging.error(f"GetUserData service Exception: {err}", exc_info=True)
            user_data_reply.valid = False
            return user_data_reply.valid

    def GetUserAddress(self, request, context):
        id = request.id
        user_address_data_reply = user_service_pb2.UserAddressArray()
        try:
            locations = Locations.objects.get(status=True, is_active=True, id=id)
            logger.info(f"locations ---->{locations}")
            user_address_data_reply.valid = True
            user_address_data_reply.user = str(locations.ref_id)
            user_address = user_service_pb2.UserAddress()
            user_address.id = str(locations.id)
            user_address.name = str(locations.name)
            user_address.latitude = str(locations.latitude)
            user_address.longitude = str(locations.longitude)
            user_address.contact_person_name = str(locations.contact_person_name)
            user_address.contact_person_phone = str(locations.contact_person_phone)
            user_address.address_one = str(locations.address_one)
            user_address.address_two = str(locations.address_two)
            user_address.city = str(locations.city)
            user_address.state = str(locations.state)
            user_address.country = str(locations.country)
            user_address.zipcode = str(locations.zipcode)
            user_address.status = locations.status
            user_address_data_reply.address_list.append(user_address)
            logger.info(f"user_address_data_reply ---->{user_address_data_reply}")
            return user_address_data_reply
        except Exception as err:
            logging.error(f"GetUserAddress service Exception: {err}", exc_info=True)
            user_address_data_reply.valid = False
            return user_address_data_reply.valid


def serve():
    print("server started")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    user_service_pb2_grpc.add_UserServicesServicer_to_server(
        UserServicesServicer(), server
    )
    server.add_insecure_port(
        cfg.get("grpc", "GRPC_USER_SERVER") + ":" + cfg.get("grpc", "GRPC_USER_PORT")
    )
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
