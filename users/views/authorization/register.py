from rest_framework.response import Response
from rest_framework import viewsets, status
from drf_yasg import openapi

from django.db import transaction
from common.helpers.common_helper import (
    random_string_generator,
    send_mail,
)
from common.helpers.errors_helper import Return400Error, Return404Error
from common.events.rabbit_mq.publisher import publish_event
from common.helpers.user_helper import getAdminCreationPayload
from common.configs.config import config as cfg
from common.swagger.documentation import (
    swagger_wrapper,
)
from organisation.serializers import OrganisationSerializer
from organisation.models import Organisations
from users.models import User, UserProfiles, UserOTPs
from users.helper import getAdminEmailPayload
from common.configs.config import config as cfg


class RegisterAPI(viewsets.ViewSet):
    http_method_names = ["post", "head", "options"]

    @swagger_wrapper(
        {
            "fname": openapi.TYPE_STRING,
            "lname": openapi.TYPE_STRING,
            "email": openapi.TYPE_STRING,
            "password": openapi.TYPE_STRING,
            "organisation": openapi.TYPE_STRING,
            "phone_number": openapi.TYPE_STRING,
            "ccode": openapi.TYPE_STRING,
            "terms_conditions": openapi.TYPE_BOOLEAN,
        },
        ["authorization"],
    )
    def create(self, request, *args, **kwargs):

        # get all required params and verify them
        required_params = [
            "fname",
            "lname",
            "email",
            "password",
            "organisation",
            "phone_number",
            "ccode",
        ]
        data = [request.data.get(key, "").strip() for key in required_params]
        if "" in data:
            return Return400Error("Some fields are missing")
        [fname, lname, email, password, organisation, phone_number, ccode] = data

        # Check whether user exists
        if User.objects.filter(email=email).count() > 0:
            return Return400Error("User with mail already exists")

        # Check whether organisation exists
        if Organisations.objects.filter(slug=organisation).count() > 0:
            return Return400Error("Organisations name already exists")

        # Check whether phone number exists
        if User.objects.filter(phone_number=phone_number, ccode=ccode).count() > 0:
            return Return400Error("User with phone number already exists")

        if not request.data.get("terms_conditions", False):
            return Return400Error("Please accept terms & conditions")

        try:
            # with transaction.atomic():
            # create organisation first
            print("trying")
            org_data = {
                "slug": organisation,
                "name": organisation,
                "email": email,
                "phone_number": phone_number,
                "ccode": ccode,
                "terms_conditions": True,
            }
            organisation_data = OrganisationSerializer(data=org_data)
            if organisation_data.is_valid():
                org_instance = organisation_data.save()
            print("organisation_data.data-->", organisation_data.data)
            print(org_instance)
            organisation_id = str(org_instance)

            print("organisation_id", organisation_id)

            # create user
            username = (
                email.split("@")[0]
                + "--ADMIN--"
                + organisation_id
                + "@"
                + email.split("@")[1]
            )
            user_data = User(
                fname=fname,
                lname=lname,
                email=email,
                phone_number=phone_number,
                ccode=ccode,
                username=username,
                organisation=organisation_id,
                utype=User.UserTypes.ADMIN,
            )
            user_data.set_password(password)
            user_data.save()
            user_id = str(user_data)
            print("115")
            # create user information
            user_information = UserProfiles(user=user_data, organisation=org_instance)
            user_information.save()
            print("121")
            # update organisation data with user info
            org_instance.created_by = user_id
            org_instance.updated_by = user_id
            org_instance.save()

            user_data.created_by = user_id
            user_data.updated_by = user_id
            user_data.save()

            # create and send activation code
            otp = random_string_generator(6)
            user_otp = UserOTPs(
                user=user_data,
                organisation=organisation_id,
                created_by=user_data,
                otp=otp,
                sent_to=email,
                used_for=UserOTPs.UsedTypes.ACTIVATE,
                sent_type=UserOTPs.SentTypes.MAIL,
            )
            user_otp.save()
            print("143")
            mail_status = publish_event(
                getAdminEmailPayload(user_data, organisation_id, otp),
                cfg.get("events", "COMMUNICATION_EXCHANGE"),
                cfg.get("events", "ADMIN_REGISTER_ROUTING_KEY"),
            )
            if not mail_status:
                # Mail sending is failed Handle the case
                print("Failed")
                pass
            # send_mail(
            #     email, otp, user_id, "User Registration"
            # )  # send email to user
        except Exception as err:
            print(err)
            return Return404Error(err)

        try:
            event_status = publish_event(
                getAdminCreationPayload(str(org_instance), cfg.get("roles", "ADMIN")),
                cfg.get("events", "USER_EXCHANGE"),
                cfg.get("events", "USER_CREATE_STAGES_ROUTING_KEY"),
            )
            if not event_status:
                # Event publishing is failed Handle the case
                pass
        except Exception as err:
            pass

        return Response(
            {
                "status": 201,
                "message": "User Created. Please Verify your mail",
                "data": {"id": user_id},
                "reload": "",
            },
            status=status.HTTP_201_CREATED,
        )
