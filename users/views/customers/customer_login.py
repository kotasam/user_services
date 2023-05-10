from rest_framework.response import Response
from rest_framework import viewsets, status
from drf_yasg import openapi
from rest_framework_simplejwt.backends import TokenBackend
from common.helpers.auth_helper import get_tokens_for_user
from common.helpers.common_helper import (
    check_mail,
    check_number,
    not_uuid,
    random_string_generator,
)

from common.helpers.errors_helper import Return400Error
from common.swagger.documentation import swagger_wrapper
from organisation.models import Organisations
from users.models import CustomerProfile, User, UserOTPs
from users.serializers import UserSerializer

MAX_OTP = 5


class CustomerLoginAPI(viewsets.ViewSet):
    http_method_names = ["post", "head", "options"]

    @swagger_wrapper(
        {
            "login_type": openapi.TYPE_STRING,
            "data": openapi.TYPE_STRING,
            "ccode": openapi.TYPE_STRING,
            "organisation": openapi.TYPE_STRING,
        },
        ["customer"],
    )
    def create(self, request, *args, **kwargs):

        login_type = request.data.get("login_type", "")
        data = request.data.get("data", "")
        ccode = request.data.get("ccode", "")
        organisation = request.data.get("organisation", "")

        send_user = ccode + data

        if not (login_type and data and organisation):
            return Return400Error("Required params are missing")

        if (
            (login_type == "email" and (ccode != "" or not check_mail(send_user)))
            or (login_type == "phone" and (ccode == "" or not check_number(send_user)))
            or login_type not in ["email", "phone"]
        ):
            return Return400Error("Invalid login type or data")

        if (
            not_uuid(organisation)
            or Organisations.objects.filter(id=organisation).count() != 1
        ):
            return Return400Error("Invalid Organisation Id")

        if (
            login_type == "phone"
            and User.objects.filter(
                phone_number=data, ccode=ccode, organisation=organisation
            ).count()
            != 0
        ):
            return Return400Error(
                "Phone number exists as staff/admin. Try another number"
            )

        if (
            login_type == "email"
            and User.objects.filter(email=data, organisation=organisation).count() != 0
        ):
            return Return400Error("Email exists as staff/admin. Try another number")

        try:
            user_otp = UserOTPs.objects.get(
                user=send_user,
                used_for=UserOTPs.UsedTypes.LOGIN,
                validated=False,
            )
            otp = user_otp.otp
        except:
            # otp = random_string_generator(6, "numeric")
            otp = "123456"
            user_otp = UserOTPs(
                user=send_user if login_type == "email" else ccode + "--" + data,
                organisation=organisation,
                created_by=send_user,
                otp=otp,
                sent_to=send_user,
                used_for=UserOTPs.UsedTypes.LOGIN,
                sent_type=UserOTPs.SentTypes.MAIL
                if login_type == "email"
                else UserOTPs.SentTypes.SMS,
                otp_count=0,
            )

        otp_count = user_otp.otp_count

        # check max otp request limit
        if otp_count >= MAX_OTP:
            return Return400Error("You reached max otp limit for today.")

        user_otp.otp_count = otp_count + 1
        user_otp.save()

        # [TODO] add send email and send otp emails

        return Response(
            {
                "status": 200,
                "message": "OTP sent successfully",
                "data": {"id": user_otp.id},
                "reload": "",
            },
            status=status.HTTP_200_OK,
        )


class CustomerOtpVerifyAPI(viewsets.ViewSet):
    http_method_names = ["post", "OPTIONS", "HEAD"]

    @swagger_wrapper(
        {"id": openapi.TYPE_STRING, "otp": openapi.TYPE_STRING},
        ["customer"],
    )
    def create(self, request, *args, **kwargs):
        id = request.data.get("id", "")
        otp = request.data.get("otp", "")

        if not_uuid(id) or len(otp) != 6:
            return Return400Error("Invalid Id")

        user_data = UserOTPs.objects.filter(id=id, otp=otp, validated=False)

        if user_data.count() != 1:
            return Return400Error("Invalid OTP or expired")
        else:
            user_data = user_data[0]

        user_data.validated = True
        user_data.save()

        email = ""
        phone_number = ""
        ccode = ""
        if user_data.sent_type == UserOTPs.SentTypes.MAIL:
            email = user_data.user
            customer = User.objects.filter(
                email=user_data.user,
                utype=User.UserTypes.ENDUSER,
                organisation=user_data.organisation,
            )
        elif user_data.sent_type == UserOTPs.SentTypes.SMS:
            phone_number = user_data.user.split("--")[1]
            ccode = user_data.user.split("--")[1]
            customer = User.objects.filter(
                phone_number=phone_number,
                ccode=ccode,
                utype=User.UserTypes.ENDUSER,
                organisation=user_data.organisation,
            )

        if not customer.count() <= 1:
            return Return400Error("Invalid User record found, please contact admin")

        if customer.count() == 1:
            user_data = customer[0]
        else:
            temp_username_value = (
                user_data.user.split("@")[1]
                if len(user_data.user.split("@")) == 2
                else ""
            )
            # create user
            username = (
                user_data.user.split("@")[0]
                + "--ENUSER--"
                + str(user_data.organisation)
                + "@"
                + temp_username_value
            )
            user_data = User(
                email=email,
                phone_number=phone_number,
                ccode=ccode,
                username=username,
                organisation=str(user_data.organisation),
                utype=User.UserTypes.ENDUSER,
                verified=True,
            )
            user_data.save()

            user_information = CustomerProfile(
                user=user_data, organisation=user_data.organisation
            )
            user_information.save()

            user_data.created_by = str(user_data)
            user_data.updated_by = str(user_data)
            user_data.save()

        customer_data = UserSerializer(user_data).data

        tokens = get_tokens_for_user(
            user_data, {"organisation": user_data.organisation, "utype": "ENDUSER"}
        )

        return Response(
            {
                "status": 200,
                "message": "Login successfully",
                "data": customer_data,
                "access_token": tokens["access"],
                "refresh_token": tokens["refresh"],
                "reload": "",
            },
            status=status.HTTP_200_OK,
        )
