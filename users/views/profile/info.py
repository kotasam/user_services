from rest_framework.response import Response
from rest_framework import viewsets, status
from drf_yasg import openapi
from common.grpc.actions.user_service_action import (
    get_organisation_data,
    get_organisation_locations,
    get_organisation_settings,
    get_organisation_staff,
    get_organisation_working_hours,
    get_user_data,
    get_user_additional_data,
    get_user_address,
    get_user_permissions,
    get_user_working_hours,
)

from common.swagger.documentation import (
    swagger_wrapper,
    swagger_auto_schema,
    id_param,
    org_param,
)
from common.helpers.errors_helper import Return400Error, Return500Error
from users.models import CustomerProfile, User, UserProfiles
from users.serializers import (
    CustomerProfilesSerializer,
    UserProfilesSerializer,
    UserSerializer,
    UserUpdateSerializer,
)


class UserInfoAPI(viewsets.ViewSet):
    http_method_names = ["get", "post", "head", "options"]
    serializer_class = UserUpdateSerializer

    @swagger_auto_schema(manual_parameters=[], tags=["profile"])
    def list(self, request, *args, **kwargs):
        try:
            user_info = User.objects.get(id=request.userinfo["id"])
            try:
                if request.userinfo["utype"] == "ENDUSER":
                    user_information = CustomerProfile.objects.get(user=user_info)
                else:
                    user_information = UserProfiles.objects.get(user=user_info)

            except:
                if request.userinfo["utype"] == "ENDUSER":
                    user_information = CustomerProfile(
                        user=user_info, organisation=request.userinfo["organisation"]
                    )
                else:
                    user_information = UserProfiles(
                        user=user_info, organisation=request.userinfo["organisation"]
                    )
                user_information.save()

            user_data = UserSerializer(user_info).data
            if request.userinfo["utype"] == "ENDUSER":
                user_information_data = CustomerProfilesSerializer(
                    user_information
                ).data
            else:
                user_information_data = UserProfilesSerializer(user_information).data

            return_data = {
                **user_information_data,
                **user_data,
                "email": user_info.email,
            }
        except:
            return Return400Error("Invalid user token provided")

        return Response(
            {
                "status": 200,
                "message": "User info",
                "data": return_data,
                "reload": "",
            },
            status=status.HTTP_200_OK,
        )

    @swagger_wrapper(
        {
            "fname": openapi.TYPE_STRING,
            "lname": openapi.TYPE_STRING,
            "phone_number": openapi.TYPE_STRING,
            "ccode": openapi.TYPE_STRING,
            "image": openapi.TYPE_STRING,
            "date_of_birth": openapi.TYPE_STRING,
            "gender": openapi.TYPE_STRING,
            "email": openapi.TYPE_STRING,
        },
        ["profile"],
    )
    def create(self, request, *args, **kwargs):

        phone_number = request.data["phone_number"]
        ccode = request.data["ccode"]
        try:
            user_info = User.objects.get(id=request.userinfo["id"])
            # Check whether phone number exists
            try:
                user_count = (
                    User.objects.filter(phone_number=phone_number, ccode=ccode)
                    .exclude(id=request.userinfo["id"])
                    .count()
                )
                if user_count > 0:
                    return Return400Error("User with phone number already exists")
            except:
                pass

            serializer = self.serializer_class(
                user_info, data=request.data, partial=True
            )

            if serializer.is_valid():
                serializer.save()
            else:
                raise Exception("Invalid User Info")

            if request.userinfo["utype"] == "ENDUSER":
                if (
                    "email" in request.data
                    and user_info.email == ""
                    and User.objects.filter(email=request.data["email"])
                    .exclude(id=request.userinfo["id"])
                    .count()
                    == 0
                ):
                    user_info.email = request.data["email"]
                    user_info.save()
                customer_profile_info = CustomerProfile.objects.get(
                    user=request.userinfo["id"]
                )
                profile_serializer = CustomerProfilesSerializer(
                    customer_profile_info,
                    data={
                        "date_of_birth": request.data.get("date_of_birth", ""),
                        "gender": request.data.get("gender", ""),
                    },
                    partial=True,
                )
                if profile_serializer.is_valid():
                    profile_serializer.save()
                else:
                    raise Exception("Invalid User Profile")

        except:
            return Return400Error("Invalid Data Provided")
        return Response(
            {
                "status": 200,
                "message": "User info updated successfully",
                "data": [],
                "reload": "",
            },
            status=status.HTTP_200_OK,
        )


class TestAPIs(viewsets.ViewSet):
    @swagger_auto_schema(manual_parameters=[id_param, org_param], tags=["profile"])
    def list(self, request, *args, **kwargs):
        id = request.query_params.get("id", "")
        org = request.query_params.get("org", "")
        orgdata = get_organisation_data(org)
        orgsettings = get_organisation_settings(org)
        orgloc = get_organisation_locations(org)
        orgstaff = get_organisation_staff(org)
        orghours = get_organisation_working_hours(org)
        user = get_user_data(id, True, True, True, True)
        useradd = get_user_additional_data(id)
        userhrs = get_user_working_hours(id)
        useraddress = get_user_address(id)
        userper = get_user_permissions(id)
        return Response(
            {
                "status": 200,
                "id": id,
                "org": org,
                "org_data": orgdata,
                "org_loc": orgloc,
                "orgsettings": orgsettings,
                "orgstaff": orgstaff,
                "orghours": orghours,
                "user": user,
                "useradd": useradd,
                "userhrs": userhrs,
                "useraddress": useraddress,
                "userper": userper,
            },
            status=status.HTTP_200_OK,
        )
