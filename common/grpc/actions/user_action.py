import grpc, os

from common.configs.config import config as cfg
from common.grpc.protopys.user_pb2_grpc import UserDataStub
from common.grpc.protopys.user_pb2 import UserId

user_grpc_host = os.getenv("RECOMMENDATIONS_HOST", cfg.get("grpc", "GRPC_USER_SERVER"))
port = cfg.get("grpc", "GRPC_USER_PORT")
users_channel = grpc.insecure_channel(f"{user_grpc_host}:{port}")

users_client = UserDataStub(users_channel)


def get_user_data(id):
    user_request = UserId(id=id)
    user_reponse = users_client.GetUser(user_request)
    return user_reponse
