# this would in user service only this is just a sample for you guys
from common.grpc.protopys import user_pb2_grpc
from common.grpc.protopys.user_pb2 import UserInfo


class UserServices(user_pb2_grpc.UserDataServicer):
    def GetUser(self, request, context):
        user_data = UserInfo(
            id="84aa2a8e-374b-41ea-b299-ec5a1b2805cb",
            fname="Client",
            lname="Admin",
            email="client@admin.com",
            ccode="+91",
            phone_number="9876543210",
            username="client.CLIENT.91964515-bf7b-46f3-b156-8ada4643160d@admin.com",
            utype="ADMIN",
            organisation="91964515-bf7b-46f3-b156-8ada4643160d",
        )
        return user_data
