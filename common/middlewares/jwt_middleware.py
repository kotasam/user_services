from django.http import HttpResponseBadRequest
import grpc, time
from rest_framework_simplejwt.backends import TokenBackend
from common.grpc.protopys.user_pb2 import UserInfo
from common.grpc.actions.user_action import get_user_data
from src.settings import JWT_SECRET


class JWTMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if self.check_url(request.path):
            response = self.get_response(request)
            return response

        auth_header = self.get_auth_header(request)
        if not isinstance(auth_header, str):
            return HttpResponseBadRequest(
                '{"status": 400, "message": "token must be provided", "data":[]}',
                status=400,
            )

        token = self.get_raw_token(auth_header)
        if not isinstance(token, str):
            return HttpResponseBadRequest(
                '{"status": 400, "message": "Invalid token format", "data":[]}',
                status=400,
            )

        (verified, payload) = self.get_token_validated(token)

        if not verified and self.check_token_expired(token):
            return HttpResponseBadRequest(
                '{"status": 403, "message": "Token expired", "data":[]}', status=403
            )
        elif not verified:
            return HttpResponseBadRequest(
                '{"status": 400, "message": "Invalid token provided", "data":[]}',
                status=400,
            )

        user_info = payload

        request.userinfo = user_info
        if not self.check_api_permission(request, user_info["id"], payload):
            return HttpResponseBadRequest(
                '{"status": 400, "message": "User doesn\'t have permission", "data":[]}',
                status=400,
            )

        response = self.get_response(request)
        return response

    def get_auth_header(self, request):
        header = request.headers.get("Authorization", None)
        if not isinstance(header, str):
            return None
        return header

    def get_raw_token(self, header):
        parts = header.split()
        if len(parts) != 2 and parts[0] != "Bearer":
            return None

        return parts[1]

    def get_token_validated(self, token):
        verified = False
        try:
            payload = TokenBackend(algorithm="HS256", signing_key=JWT_SECRET).decode(
                token, verify=True
            )
            verified = True
        except:
            payload = []

        return (verified, payload)

    def epoch_time(self):
        return int(time.time())

    def check_token_expired(self, token):
        try:
            payload = TokenBackend(algorithm="HS256", signing_key=JWT_SECRET).decode(
                token, verify=False
            )
            if "exp" in payload and payload["exp"] < self.epoch_time():
                return True
        except:
            pass

        return False

    def check_url(self, path):
        if (
            path == "/"
            or path == "/users/docs"
            or path == "/users/silk"
            or path == "/users/prometheus-worke/metrics"
        ):
            return True

        url = path.split("/")
        if len(url) == 2:
            return False
        return url[2] in self.allowed_urls()

    def allowed_urls(self):
        return ["authorisation", "customer", "silkrequest", "silk"]

    def customer_allowed_urls(self, path):
        return path.split("/")[3] in ["address", "info"]

    def check_api_permission(self, request, user_id, payload):
        if payload["utype"] == "ENDUSER":
            return self.customer_allowed_urls(request.path)

        if payload["utype"] == "STAFF":
            return self.staff_api_permissions(request, payload)
        return True

    def staff_api_permissions(self, request, payload):
        if (
            payload["role"] == "Manager"
            and request.method in ["GET", "PUT", "POST"]
            and request.path == "/users/staff/information/"
        ):
            return True
        elif request.path == "/users/profile/info/":
            return True

        return False
