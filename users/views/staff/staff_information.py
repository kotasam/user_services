from rest_framework import viewsets, status
from rest_framework.response import Response
from drf_yasg import openapi
from django.utils import timezone
from django.db.models import Q

from common.helpers.common_helper import random_string_generator, send_mail
from common.swagger.documentation import swagger_auto_schema, swagger_wrapper
from common.helpers.errors_helper import Return400Error, Return404Error, Return500Error
from common.events.rabbit_mq.publisher import publish_event
from common.configs.config import config as cfg
from users.helper import getStaffCreationEmailPayload, getStaffPayloadForAudit
from organisation.models import Departments, RolesPermissions
from users.models import User, UserDepartments, UserProfiles, UserOTPs
from users.serializers import (
    StaffSerializer,
    UserUpdateSerializer,
    UserProfilesSerializer,
    UserSerializer,
    StaffListSerializer,
)
import logging


class StaffInformationAPI(viewsets.ViewSet):
    http_method_names = ["post", "get", "delete", "put", "head", "options"]
    serializer_class = StaffSerializer

    @swagger_auto_schema(manual_parameters=[], tags=["staff"])
    def list(self, request, *args, **kwargs):
        staff_query_set = Q(
            is_active=True,
            organisation=request.userinfo["organisation"],
            utype=User.UserTypes.STAFF,
        )
        staffs_information = User.objects.filter(staff_query_set)
        staffs_data = StaffListSerializer(staffs_information, many=True).data
        try:
            admin_query_set = Q(
                is_active=True,
                organisation=request.userinfo["organisation"],
                utype=User.UserTypes.ADMIN,
            )
            admin_information = User.objects.get(admin_query_set)
            admin_data = StaffListSerializer(admin_information).data
            staffs_data.append(admin_data)
        except Exception as err:
            logging.error(f"StaffInformationAPI list: {err}", exc_info=True)
            # return Return500Error("Internal error, try again after some time.")
        return Response(
            {
                "status": 200,
                "message": "Staff list",
                "data": staffs_data,
                "reload": "",
            },
            status=status.HTTP_200_OK,
        )

    @swagger_wrapper(
        {
            "fname": openapi.TYPE_STRING,
            "lname": openapi.TYPE_STRING,
            "email": openapi.TYPE_STRING,
            "password": openapi.TYPE_STRING,
            "phone_number": openapi.TYPE_STRING,
            "ccode": openapi.TYPE_STRING,
            "department": openapi.TYPE_STRING,
            "role": openapi.TYPE_STRING,
        },
        ["staff"],
    )
    def create(self, request, *args, **kwargs):
        try:
            fname = request.data["fname"]
            lname = request.data["lname"]
            email = request.data["email"]
            password = request.data["password"]
            role = request.data["role"]
            phone_number = request.data["phone_number"]
            ccode = request.data["ccode"]
            organisation = request.userinfo["organisation"]

            # Check whether email exists
            try:
                User.objects.get(email=email)
                return Return400Error("User with mail already exists")
            except:
                pass

            # Check whether phone number exists
            try:
                User.objects.get(phone_number=phone_number, ccode=ccode)
                return Return400Error("User with phone number already exists")
            except:
                pass

            # Check whether role exists
            try:
                if "role" in request.data and request.data["role"] != "":

                    role = RolesPermissions.objects.get(
                        id=request.data["role"],
                        status=True,
                        is_active=True,
                        organisation=request.userinfo["organisation"],
                    )
                else:
                    role = ""
            except:
                return Return400Error("Invalid role sent")

            # Check whether department exists
            try:
                department = Departments.objects.get(
                    id=request.data["department"], status=True, is_active=True
                )
            except Exception as err:
                return Return400Error("Invalid department sent")

            # create username
            username = (
                email.split("@")[0]
                + "--STAFF--"
                + str(organisation)
                + "@"
                + email.split("@")[1]
            )

            staff_info = User(
                fname=fname,
                lname=lname,
                email=email,
                phone_number=phone_number,
                ccode=ccode,
                organisation=organisation,
                username=username,
                utype=User.UserTypes.STAFF,
                source=User.SourceTypes.MANUAL,
                created_by=request.userinfo["id"],
                updated_by=request.userinfo["id"],
            )

            staff_info.set_password(password)
            staff_info.save()

            # create user information
            user_information = UserProfiles(
                user=staff_info,
                organisation=organisation,
                role=role,
                department=department,
            )
            user_information.save()

            # create and send activation code
            otp = random_string_generator(16)
            user_otp = UserOTPs(
                user=staff_info,
                organisation=organisation,
                created_by=staff_info,
                otp=otp,
                sent_to=email,
                used_for=UserOTPs.UsedTypes.ACTIVATE,
                sent_type=UserOTPs.SentTypes.MAIL,
            )
            user_otp.save()

            # send_mail(email, otp, str(staff_info))  # send email to user
            mail_status = publish_event(
                getStaffCreationEmailPayload(staff_info, password),
                cfg.get("events", "COMMUNICATION_EXCHANGE"),
                cfg.get("events", "STAFF_REGISTER_ROUTING_KEY"),
            )
            if not mail_status:
                # Mail sending is failed Handle the case
                pass

            # staff_flag = False
            # if "departments" in request.data and len(request.data["departments"]) != 0:
            #     try:
            #         departments_list = []
            #         for department in set(request.data["departments"]):
            #             try:
            #                 department_info = Departments.objects.get(
            #                     id=department,
            #                     organisation=organisation,
            #                     is_active=True,
            #                     status=True,
            #                 )
            #                 departments_list.append(
            #                     UserDepartments(
            #                         user=staff_info,
            #                         department=department_info,
            #                         organisation=organisation,
            #                         created_by=request.userinfo["id"],
            #                         updated_by=request.userinfo["id"],
            #                     )
            #                 )
            #             except:
            #                 staff_flag = True

            #         UserDepartments.objects.bulk_create(departments_list)
            #     except:
            #         staff_flag = True

            staff_data = self.serializer_class(staff_info).data

            event_status = publish_event(
                getStaffPayloadForAudit(staff_info),
                cfg.get("events", "AUDIT_SERVICE_EXCHANGE"),
                cfg.get("events", "AUDIT_SERVICE_STAFF_CREATE_ROUTING_KEY"),
            )
            if not event_status:
                # Handle the failed the case
                pass
            return Response(
                {
                    "status": 201,
                    "message": "Staff created successfully",
                    "data": staff_data,
                    "reload": "",
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as err:
            return Return500Error("Internal error, try again after some time.")

    @swagger_auto_schema(manual_parameters=[], tags=["staff"])
    def retrieve(self, request, *args, **kwargs):
        try:
            staff_id = kwargs["pk"]

            try:
                staff_info = User.objects.get(
                    id=staff_id,
                    is_active=True,
                    organisation=request.userinfo["organisation"],
                )
            except:
                return Return404Error("Staff not found")

            try:
                user_information = UserProfiles.objects.get(user=staff_info)
            except:
                user_information = UserProfiles(
                    user=staff_info, organisation=request.userinfo["organisation"]
                )
                user_information.save()

            user_data = StaffListSerializer(staff_info).data
            user_information_data = UserProfilesSerializer(user_information).data

            return_data = {**user_information_data, **user_data}

            return Response(
                {
                    "status": 200,
                    "message": "User info",
                    "data": return_data,
                    "reload": "",
                },
                status=status.HTTP_200_OK,
            )
        except:
            return Return500Error("Internal error, try again after some time.")

    @swagger_wrapper(
        {
            "fname": openapi.TYPE_STRING,
            "lname": openapi.TYPE_STRING,
            "phone_number": openapi.TYPE_STRING,
            "ccode": openapi.TYPE_STRING,
            "departments": openapi.TYPE_OBJECT,
            "role": openapi.TYPE_STRING,
            "date_of_birth": openapi.TYPE_STRING,
            "gender": openapi.TYPE_STRING,
            "designation": openapi.TYPE_STRING,
            "specialisation": openapi.TYPE_STRING,
            "age": openapi.TYPE_STRING,
            "experience": openapi.TYPE_STRING,
            "qualification": openapi.TYPE_STRING,
            "description": openapi.TYPE_STRING,
        },
        ["staff"],
    )
    def update(self, request, *args, **kwargs):
        try:
            staff_id = kwargs["pk"]
            try:
                staff_info = User.objects.get(
                    id=staff_id,
                    is_active=True,
                    organisation=request.userinfo["organisation"],
                )
                user_info = UserProfiles.objects.get(user=staff_info)
            except:
                return Return404Error("Staff not found")

            if "status" in request.data and len(request.data) == 1:
                staff_info.status = request.data.get("status")
                staff_info.save()
                event_status = publish_event(
                    getStaffPayloadForAudit(staff_info),
                    cfg.get("events", "AUDIT_SERVICE_EXCHANGE"),
                    cfg.get("events", "AUDIT_SERVICE_STAFF_UPDATE_ROUTING_KEY"),
                )
                if not event_status:
                    # Handle the failed the case
                    pass
                return Response(
                    {
                        "status": 200,
                        "message": "User status updated successfully",
                        "data": {},
                        "reload": "",
                    },
                    status=status.HTTP_200_OK,
                )

            phone_number = request.data["phone_number"]
            ccode = request.data["ccode"]

            # Check whether phone number exists
            try:
                User.objects.get(phone_number=phone_number, ccode=ccode).exclude(
                    id=staff_id
                )
                return Return400Error("User with phone number already exists")
            except:
                pass

            # Check whether department exists
            try:
                if (
                    "department" in request.data
                    and staff_info.utype != User.UserTypes.ADMIN
                ):
                    Departments.objects.get(
                        id=request.data["department"], status=True, is_active=True
                    )
            except:
                return Return400Error("Invalid department sent")

            # Check whether role exists
            try:
                if "role" in request.data and staff_info.utype != User.UserTypes.ADMIN:
                    RolesPermissions.objects.get(
                        id=request.data["role"], status=True, is_active=True
                    )
            except:
                return Return400Error("Invalid role sent")

            if staff_info.utype != User.UserTypes.ADMIN:
                del request.data["role"]

            # staff_flag = False
            # if "departments" in request.data and len(request.data["departments"]) != 0:
            #     try:
            #         existing_departments = UserDepartments.objects.filter(
            #             user=staff_info.id,
            #             organisation=request.userinfo["organisation"],
            #         )
            #         existing_departments.delete()

            #         departments_list = []
            #         for department in set(request.data["departments"]):
            #             try:
            #                 department_info = Departments.objects.get(
            #                     id=department,
            #                     organisation=request.userinfo["organisation"],
            #                     is_active=True,
            #                     status=True,
            #                 )
            #                 departments_list.append(
            #                     UserDepartments(
            #                         user=staff_info,
            #                         department=department_info,
            #                         organisation=request.userinfo["organisation"],
            #                         created_by=request.userinfo["id"],
            #                         updated_by=request.userinfo["id"],
            #                     )
            #                 )
            #             except:
            #                 staff_flag = True
            #         UserDepartments.objects.bulk_create(departments_list)
            #     except:
            #         staff_flag = True

            serializer = UserUpdateSerializer(
                staff_info, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()

            user_info_serializer = UserProfilesSerializer(
                user_info, data=request.data, partial=True
            )
            if user_info_serializer.is_valid():
                user_info_serializer.save()

            return_data = {**serializer.data, **user_info_serializer.data}
            event_status = publish_event(
                getStaffPayloadForAudit(staff_info),
                cfg.get("events", "AUDIT_SERVICE_EXCHANGE"),
                cfg.get("events", "AUDIT_SERVICE_STAFF_UPDATE_ROUTING_KEY"),
            )
            if not event_status:
                # Handle the failed the case
                pass

            return Response(
                {
                    "status": 200,
                    "message": "User info updated successfully",
                    "data": return_data,
                    "reload": "",
                },
                status=status.HTTP_200_OK,
            )
        except Exception as err:
            logging.error(f"StaffInformationAPI update: {err}", exc_info=True)
            return Return500Error("Internal error, try again after sometime.")

    @swagger_auto_schema(manual_parameters=[], tags=["staff"])
    def destroy(
        self, request, *args, **kwargs
    ):  # [TODO] check few paramter before deleting them.
        try:
            staff_id = kwargs["pk"]
            try:
                staff_info = User.objects.get(
                    id=staff_id,
                    is_active=True,
                    organisation=request.userinfo["organisation"],
                ).exclude(utype=User.UserTypes.ADMIN)
                user_info = UserProfiles.objects.get(user=staff_info)
            except:
                return Return404Error("Staff not found")

            staff_info.is_active = False
            staff_info.deleted_by = request.userinfo["id"]
            staff_info.deleted_at = timezone.now()
            staff_info.save()

            user_info.is_active = False
            user_info.deleted_by = request.userinfo["id"]
            user_info.deleted_at = timezone.now()
            user_info.save()

            event_status = publish_event(
                getStaffPayloadForAudit(staff_info),
                cfg.get("events", "AUDIT_SERVICE_EXCHANGE"),
                cfg.get("events", "AUDIT_SERVICE_STAFF_DELETE_ROUTING_KEY"),
            )
            if not event_status:
                # Handle the failed the case
                pass

            return Response(
                {
                    "status": 200,
                    "message": "User deleted successfully",
                    "data": [],
                    "reload": "",
                },
                status=status.HTTP_200_OK,
            )
        except:
            return Return500Error("Internal error, try after some time")
