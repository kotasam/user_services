import grpc
from common.grpc.protopys import crm_pb2_grpc, crm_pb2
from common.configs.config import config as cfg


def getContactInfo(source_id, department, organisation):
    try:
        host = cfg.get("grpc", "GRPC_CRM_SERVER")
        port = cfg.get("grpc", "GRPC_CRM_PORT")
        with grpc.insecure_channel(f"{host}:{port}") as channel:
            stub = crm_pb2_grpc.ContactDataStub(channel)
            contact_info_request = crm_pb2.ContactInfoRequest(
                contact_id=source_id, department=department, organisation=organisation
            )
            user_info_reply = stub.GetContact(contact_info_request)
            if not user_info_reply.valid:
                return None
            return {
                "id": user_info_reply.id,
                "department": user_info_reply.department,
                "organisation": user_info_reply.organisation,
                "first_name": user_info_reply.first_name,
                "last_name": user_info_reply.last_name,
                "email": user_info_reply.email,
                "phone_number": user_info_reply.phone_number,
                "title": user_info_reply.title,
                "owner": user_info_reply.owner,
                "designation": user_info_reply.designation,
                "tags": user_info_reply.tags,
                "company": user_info_reply.company,
            }
    except Exception as err:
        print("In exception --->", err)
        return None
