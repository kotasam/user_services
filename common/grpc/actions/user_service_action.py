import grpc
import os
from google.protobuf.json_format import MessageToDict

from common.configs.config import config as cfg
from common.grpc.protopys.user_service_pb2_grpc import UserServicesStub
from common.grpc.protopys.user_service_pb2 import (
    UserItem,
    IdItem,
    OrganisationData,
    OrganisationLocations,
    OrganisationSettings,
    WorkingHours,
    UserData,
    UserAdditionalData,
    UserAddressArray,
    UserPermissions,
    OrganisationStaffs,
)


user_grpc_host = os.getenv("RECOMMENDATIONS_HOST", cfg.get("grpc", "GRPC_USER_SERVER"))
port = cfg.get("grpc", "GRPC_USER_PORT")
users_channel = grpc.insecure_channel(f"{user_grpc_host}:{port}")

user_service_client = UserServicesStub(users_channel)


def get_organisation_data(id):
    request = IdItem(id=id)
    try:
        return MessageToDict(user_service_client.GetOrganisation(request))
    except grpc._channel._InactiveRpcError as err:
        return MessageToDict(
            OrganisationData(
                valid=True,
                id=id,
                slug="slug",
                name="name",
                description="description",
                email="email",
                phone_number="phone_number",
                ccode="ccode",
                image="image",
                website="website",
                address="address",
                identifier="identifier",
                registration_id="registration_id",
            )
        )


def get_organisation_locations(id):
    request = IdItem(id=id)
    try:
        return MessageToDict(user_service_client.GetOrganisationLocations(request))
    except grpc._channel._InactiveRpcError as err:
        return MessageToDict(OrganisationLocations())


def get_organisation_settings(id):
    request = IdItem(id=id)
    try:
        return MessageToDict(user_service_client.GetOrganisationSettings(request))
    except grpc._channel._InactiveRpcError as err:
        return MessageToDict(OrganisationSettings())


def get_organisation_staff(id):
    request = IdItem(id=id)
    try:
        return MessageToDict(user_service_client.GetOrganisationStaff(request))
    except grpc._channel._InactiveRpcError as err:
        return MessageToDict(OrganisationStaffs())


def get_organisation_working_hours(id):
    request = IdItem(id=id)
    try:
        return MessageToDict(user_service_client.GetOrganisationWorkingHours(request))
    except grpc._channel._InactiveRpcError as err:
        return MessageToDict(WorkingHours())


def get_user_data(
    id,
    organisation=False,
    user_additional=False,
    user_permissions=False,
    user_working_hours=False,
):
    request = UserItem(
        id=id,
        organisation=organisation,
        user_additional=user_additional,
        user_permissions=user_permissions,
        user_working_hours=user_working_hours,
    )
    try:
        return MessageToDict(user_service_client.GetUserData(request))
    except grpc._channel._InactiveRpcError as err:
        return MessageToDict(UserData())


def get_user_additional_data(id):
    request = IdItem(id=id)
    try:
        return MessageToDict(user_service_client.GetUserAdditionalData(request))
    except grpc._channel._InactiveRpcError as err:
        return MessageToDict(UserAdditionalData())


def get_user_working_hours(id):
    request = IdItem(id=id)
    try:
        return MessageToDict(user_service_client.GetUserWorkingHours(request))
    except grpc._channel._InactiveRpcError as err:
        return MessageToDict(WorkingHours())


def get_user_address(id):
    request = IdItem(id=id)
    try:
        return MessageToDict(user_service_client.GetUserAddress(request))
    except grpc._channel._InactiveRpcError as err:
        return MessageToDict(UserAddressArray())


def get_user_permissions(id):
    request = IdItem(id=id)
    try:
        return MessageToDict(user_service_client.GetUserPermissions(request))
    except grpc._channel._InactiveRpcError as err:
        return MessageToDict(UserPermissions())
