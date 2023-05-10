from common.grpc.protopys.user_service_pb2_grpc import UserServicesServicer
from common.grpc.protopys.user_service_pb2 import (
    OrganisationData,
    UserData,
    UserAdditionalData,
    OrganisationSettings,
    WorkingHours,
    OrganisationStaffs,
    OrganisationLocations,
    ArrayOfLocations,
    UserAddressArray,
    UserAddress,
    UserPermissions,
    ArrayOfSlots,
    ArrayofTimes,
    IdNameData,
)
from organisation.models import (
    Locations,
    Organisations,
    GeneralSettings,
    RolesPermissions,
    WorkingHours as OrganisationWorkingHoursModel,
)
from organisation.serializers import (
    LocationsSerializer,
    OrganisationGRPCSerializer,
    GeneralSettingsSerializer,
    RolesPermissionSerializer,
    WorkingHourSerializer,
)
from users.models import User, UserProfiles
from users.serializers import (
    StaffSerializer,
    UserAddressSerializer,
    UserGRPCSerializer,
    UserProfilesSerializer,
)


def organisation_data(id):
    try:
        organisation_info = Organisations.objects.get(id=id, is_active=True)
        serialize_data = OrganisationGRPCSerializer(organisation_info).data
    except:
        serialize_data = {}

    is_valid = True if serialize_data else False
    data = OrganisationData(
        valid=is_valid,
        id=id,
        slug=serialize_data.get("slug", "Null"),
        name=serialize_data.get("name", "Null"),
        description=serialize_data.get("description", "Null"),
        email=serialize_data.get("email", "Null"),
        phone_number=serialize_data.get("phone_number", "Null"),
        ccode=serialize_data.get("ccode", "Null"),
        image=serialize_data.get("image", "Null"),
        website=serialize_data.get("website", "Null"),
        address=serialize_data.get("address", "Null"),
        identifier=serialize_data.get("identifier", "Null"),
        registration_id=serialize_data.get("registration_id", "Null"),
    )
    return data


def organisation_settings_data(id):

    try:
        organisation_settings_info = GeneralSettings(organisation=id, is_active=True)
        serialize_data = GeneralSettingsSerializer(organisation_settings_info).data
    except:
        serialize_data = []

    return OrganisationSettings(
        valid=True if serialize_data else False,
        id=id,
        country=serialize_data.get("country", ""),
        currency=serialize_data.get("currency", ""),
        ccode=serialize_data.get("ccode", ""),
        timezone=serialize_data.get("timezone", ""),
        dateformat=serialize_data.get("dateformat", ""),
        timeformat=serialize_data.get("timeformat", ""),
        slot_duration=serialize_data.get("slot_duration", ""),
    )


def working_hours_data(
    id, type=OrganisationWorkingHoursModel.WorkingHourTypes.ORGANISATION
):
    try:
        organisation_working_hours_info = OrganisationWorkingHoursModel.objects.filter(
            ref_id=id, type=type
        )
        if organisation_working_hours_info.count() < 7:
            serialize_data = []
        else:
            serialize_data = WorkingHourSerializer(
                organisation_working_hours_info, many=True
            ).data

    except:
        serialize_data = []

    return WorkingHours(
        valid=True if serialize_data else False,
        id=id,
        monday=ArrayOfSlots(
            slots=[
                ArrayofTimes(start=slot[0], end=slot[1])
                for slot in serialize_data[0].get("slots", [])
            ]
        ),
        tuesday=ArrayOfSlots(
            slots=[
                ArrayofTimes(start=slot[0], end=slot[1])
                for slot in serialize_data[1].get("slots", [])
            ]
        ),
        wednesday=ArrayOfSlots(
            slots=[
                ArrayofTimes(start=slot[0], end=slot[1])
                for slot in serialize_data[2].get("slots", [])
            ]
        ),
        thursday=ArrayOfSlots(
            slots=[
                ArrayofTimes(start=slot[0], end=slot[1])
                for slot in serialize_data[3].get("slots", [])
            ]
        ),
        friday=ArrayOfSlots(
            slots=[
                ArrayofTimes(start=slot[0], end=slot[1])
                for slot in serialize_data[4].get("slots", [])
            ]
        ),
        saturday=ArrayOfSlots(
            slots=[
                ArrayofTimes(start=slot[0], end=slot[1])
                for slot in serialize_data[5].get("slots", [])
            ]
        ),
        sunday=ArrayOfSlots(
            slots=[
                ArrayofTimes(start=slot[0], end=slot[1])
                for slot in serialize_data[6].get("slots", [])
            ]
        ),
    )


def organisation_staff_data(id):
    try:
        organisation_staff_info = User.objects.filter(is_active=True, organisation=id)
        serialize_data = StaffSerializer(organisation_staff_info, many=True).data
    except:
        serialize_data = []

    try:

        return OrganisationStaffs(
            valid=True if serialize_data else False,
            id=id,
            staffs=[
                UserData(
                    valid=True,
                    id=staff.get("id", ""),
                    fname=staff.get("fname", ""),
                    lname=staff.get("lname", ""),
                    username=staff.get("username", ""),
                    email=staff.get("email", ""),
                    phone_number=staff.get("phone_number", ""),
                    ccode=staff.get("ccode", ""),
                    image=staff.get("image", ""),
                    utype=staff.get("utype", ""),
                    status=staff.get("status", False),
                    organisation=staff.get("organisation", ""),
                )
                for staff in serialize_data
            ],
        )
    except:
        return OrganisationStaffs()


def organisation_locations_info(id):
    try:
        organisation_locations_data = Locations.objects.filter(
            organisation=id,
            is_active=True,
            ltype=Locations.LocationTypes.ORGANISATION,
            ref_id=id,
        )
        serialize_data = LocationsSerializer(
            organisation_locations_data, many=True
        ).data
    except:
        serialize_data = []
    try:
        return OrganisationLocations(
            valid=True if serialize_data else False,
            id=id,
            locations=[
                ArrayOfLocations(
                    id=location.get("id", ""),
                    name=location.get("name", ""),
                    location=location.get("location", ""),
                    status=location.get("status", None),
                )
                for location in serialize_data
            ],
        )
    except:
        return OrganisationLocations(valid=True if serialize_data else False, id=id)


def user_data(
    id, is_organisation, is_user_additional, is_user_permissions, is_user_working_hours
):
    try:
        user_info = User.objects.get(id=id, is_active=True)
        serialize_data = UserGRPCSerializer(user_info).data
    except:
        serialize_data = []

    organisation_info = OrganisationData()
    user_additional_info = UserAdditionalData()
    user_permissions_info = UserPermissions()
    user_working_hours_info = WorkingHours()

    if is_organisation:
        organisation_info = organisation_data(serialize_data.get("organisation", ""))

    if is_user_additional:
        user_additional_info = user_additional_data(id)

    if is_user_working_hours:
        user_working_hours_info = working_hours_data(
            id, OrganisationWorkingHoursModel.WorkingHourTypes.USER
        )

    if is_user_permissions:
        user_permissions_info = user_permissions_data(id)

    try:
        return UserData(
            valid=True if serialize_data else False,
            id=id,
            fname=serialize_data.get("fname", ""),
            lname=serialize_data.get("lname", ""),
            username=serialize_data.get("username", ""),
            email=serialize_data.get("email", ""),
            phone_number=str(serialize_data.get("phone_number", "")),
            ccode=str(serialize_data.get("ccode", "")),
            image=serialize_data.get("image", ""),
            utype=serialize_data.get("utype", ""),
            status=serialize_data.get("status", ""),
            organisation=serialize_data.get("organisation", ""),
            organisation_data=organisation_info,
            user_additional_data=user_additional_info,
            user_permissions=user_permissions_info,
            user_working_hours=user_working_hours_info,
        )
    except:
        return UserData()


def user_additional_data(id):
    try:
        user_additional_info = UserProfiles.objects.get(user=id, is_active=True)
        serialize_data = UserProfilesSerializer(user_additional_info).data
    except:
        serialize_data = []

    return UserAdditionalData(
        valid=True if serialize_data else False,
        id=id,
        date_of_birth=serialize_data.get("date_of_birth", ""),
        gender=serialize_data.get("gender", ""),
        designation=serialize_data.get("designation", ""),
        specialisation=serialize_data.get("specialisation", ""),
        age=serialize_data.get("age", ""),
        experience=serialize_data.get("experience", ""),
        qualification=serialize_data.get("qualification", ""),
        description=serialize_data.get("description", ""),
        role=IdNameData(id=str(serialize_data.get("role", ""))),
        department=IdNameData(id=str(serialize_data.get("department", ""))),
    )


def user_address_data(id):
    try:
        user_address_info = Locations.objects.filter(
            is_active=True,
            ref_id=id,
            ltype=Locations.LocationTypes.USER,
            # organisation=request.userinfo["organisation"],
        )
        serialize_data = UserAddressSerializer(user_address_info, many=True).data
    except:
        serialize_data = []

    try:
        return UserAddressArray(
            valid=True if serialize_data else False,
            user=id,
            address_list=[
                UserAddress(
                    id=address.get("id", ""),
                    name=address.get("name", ""),
                    latitude=address.get("latitude", ""),
                    longitude=address.get("longitude", ""),
                    contact_person_name=address.get("contact_person_name", ""),
                    contact_person_phone=address.get("contact_person_phone", ""),
                    address_one=address.get("address_one", ""),
                    address_two=address.get("address_two", ""),
                    city=address.get("city", ""),
                    state=address.get("state", ""),
                    country=address.get("country", ""),
                    zipcode=address.get("zipcode", ""),
                    status=address.get("status", ""),
                )
                for address in serialize_data
            ],
        )
    except:
        return UserAddressArray()


def user_permissions_data(id):
    try:
        user_additional_info = UserProfiles.objects.get(user=id, is_active=True)
        roles_permissions_info = RolesPermissions.objects.get(
            id=str(user_additional_info.role)
        )
        serialize_data = RolesPermissionSerializer(roles_permissions_info).data

    except:
        serialize_data = []

    return UserPermissions(
        valid=True if serialize_data else False,
        user=id,
        name=serialize_data.get("name", ""),
        permissions=str(serialize_data.get("permissions", "")),
        status=serialize_data.get("status", ""),
    )


class UserServices(UserServicesServicer):
    def GetOrganisation(self, request, context):
        return organisation_data(request.id)

    def GetOrganisationSettings(self, request, context):
        return organisation_settings_data(request.id)

    def GetOrganisationWorkingHours(self, request, context):
        return working_hours_data(request.id)

    def GetOrganisationStaff(self, request, context):
        return organisation_staff_data(request.id)

    def GetOrganisationLocations(self, request, context):
        return organisation_locations_info(request.id)

    def GetUserData(self, request, context):
        return user_data(
            request.id,
            request.organisation,
            request.user_additional,
            request.user_permissions,
            request.user_working_hours,
        )

    def GetUserAdditionalData(self, request, context):
        return user_additional_data(request.id)

    def GetUserAddress(self, request, context):
        return user_address_data(request.id)

    def GetUserWorkingHours(self, request, context):
        return working_hours_data(
            request.id, type=OrganisationWorkingHoursModel.WorkingHourTypes.USER
        )

    def GetUserPermissions(self, request, context):
        return user_permissions_data(request.id)
