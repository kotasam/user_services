from rest_framework.response import Response
from rest_framework import viewsets, status
from common.helpers.common_helper import send_mail


from common.helpers.errors_helper import Return400Error
from common.swagger.documentation import swagger_auto_schema, email_param, code_param
from users.models import User, UserOTPs

MAX_OTP = 5


class ActivateUserAPI(viewsets.ViewSet):
    http_method_names = ["get", "head", "options"]

    @swagger_auto_schema(manual_parameters=[code_param], tags=["authorization"])
    def retrieve(self, request, *args, **kwargs):
        code = request.query_params.get("code", "")
        user_id = kwargs.get("pk", "")

        if not (code and user_id):
            return Return400Error("Some fields are missing.")

        try:
            # get user information
            user_info = User.objects.get(id=user_id)
            if user_info.verified:
                return Return400Error("User already activated please login")

            # check for whether code is correct or not
            user_otp_info = UserOTPs.objects.get(
                user=user_id,
                otp=code,
                validated=False,
                used_for=UserOTPs.UsedTypes.ACTIVATE,
            )

            # [TODO]: check for time limit during validation
            # if not user_otp_info:
            #     return Return400Error("Invalid code or link got expired")

            user_otp_info.validated = True
            user_otp_info.save()

            user_info.verified = True  # activate user
            user_info.save()

            return Response(
                {
                    "status": 200,
                    "message": "User account activated. Redirect to login",
                    "data": [],
                    "reload": "/login",
                },
                status=status.HTTP_200_OK,
            )

        except Exception as err:
            return Return400Error("Invalid code or link got expired")


class ResendActivationAPI(viewsets.ViewSet):
    http_method_names = ["get", "head", "options"]

    @swagger_auto_schema(manual_parameters=[email_param], tags=["authorization"])
    def list(self, request, *args, **kwargs):
        email = request.query_params.get("email", "")
        if not email:
            return Return400Error("Invalid Email sent")

        try:
            user_otp = UserOTPs.objects.get(
                sent_to=email,
                used_for=UserOTPs.UsedTypes.ACTIVATE,
                sent_type=UserOTPs.SentTypes.MAIL,
                validated=False,
            )
            otp = user_otp.otp
        except:
            return Return400Error("Invalid Email Sent")

        otp_count = user_otp.otp_count

        # check max otp request limit
        if otp_count >= MAX_OTP:
            return Return400Error("You reached max otp limit for today.")

        user_otp.otp_count = otp_count + 1
        user_otp.save()

        send_mail(email, otp, user_otp.user, "Account Activation")

        return Response({"status": 200, "message": "OTP sent Successfully", "data": []})
