from rest_framework.response import Response
from rest_framework import viewsets, status
from drf_yasg import openapi
from rest_framework_simplejwt.backends import TokenBackend
from drf_yasg.utils import swagger_auto_schema


from common.helpers.auth_helper import get_tokens_for_user
from common.helpers.errors_helper import Return400Error
from common.swagger.documentation import swagger_wrapper, token_param
from users.models import User
from users.serializers import UserSerializer


class LoginAPI(viewsets.ViewSet):
    http_method_names = ["post", "head", "options"]

    @swagger_wrapper(
        {"email": openapi.TYPE_STRING, "password": openapi.TYPE_STRING},
        ["authorization"],
    )
    def create(self, request, *args, **kwargs):

        # required_params = ["email", "password"]
        email = request.data.get("email", "")
        password = request.data.get("password", "")
        if not (email and password):
            return Return400Error("Required params are missing")

        initial_setup = False

        try:
            # check for active user record.
            user_info = User.objects.get(email=email, is_active=True, status=True)

            # check whether verified or not.
            if not user_info.verified:
                return Return400Error(
                    "Please activate user account.",
                    {"id": user_info.id, "email": user_info.email},
                    "/verify",
                )

            # validate user password.
            if not user_info.check_password(password):
                raise Exception("Invalid Password")

            user = UserSerializer(user_info).data

            # get jwt tokens
            tokens = get_tokens_for_user(
                user_info,
                {"organisation": user["organisation"], "utype": user["utype"]},
            )
        except Exception as err:
            return Return400Error("Invalid credentials")

        # for redirecting user to onboarding screen
        if user_info.initial_setup:
            user_info.initial_setup = False
            user_info.save()
            initial_setup = True

        return Response(
            {
                "status": 200,
                "message": "Login Successfull",
                "data": user,
                "access_token": tokens["access"],
                "refresh_token": tokens["refresh"],
                "initial_setup": initial_setup,
                "reload": "/getting-started" if initial_setup else "/dashboard",
            },
            status=status.HTTP_200_OK,
        )


class VerifyUserAPI(viewsets.ViewSet):
    http_method_names = ["get", "head", "options"]

    @swagger_auto_schema(manual_parameters=[], tags=["authorization"])
    def list(self, request, *args, **kwargs):
        # get jwt token from headers
        header = request.headers.get("Authorization", None)
        if not isinstance(header, str):
            return Return400Error("Token not provided.")

        parts = header.split()
        if len(parts) != 2 and parts[0] != "Bearer":
            return Return400Error("Invalid token format")
        token = parts[1]

        try:
            payload = TokenBackend(algorithm="HS256").decode(token, verify=False)
            user_info = User.objects.get(
                id=payload["id"], is_active=True, status=True, verified=True
            )
            return_user_data = UserSerializer(user_info).data
        except:
            return Return400Error("Invalid user or token")

        return Response(
            {
                "status": 200,
                "message": "user details",
                "data": return_user_data,
                "reload": "",
            },
            status=status.HTTP_200_OK,
        )


class RefreshTokenAPI(viewsets.ViewSet):
    http_method_names = ["get", "head", "options"]

    @swagger_auto_schema(manual_parameters=[token_param], tags=["authorization"])
    def list(self, request, *args, **kwargs):
        return Response(
            {"status": 200, "message": "user details", "data": [], "reload": ""},
            status=status.HTTP_200_OK,
        )
