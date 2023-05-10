from rest_framework import viewsets, status
from rest_framework.response import Response
from django.utils import timezone
from drf_yasg import openapi

from organisation.models import Locations as Address
from common.swagger.documentation import swagger_auto_schema, swagger_wrapper
from common.helpers.errors_helper import Return404Error, Return500Error, Return400Error
from users.serializers import UserAddressSerializer


class UserAddressAPI(viewsets.ViewSet):
    http_method_names = ["get", "post", "put", "delete", "head", "options"]
    serializer_class = UserAddressSerializer

    @swagger_auto_schema(manual_parameters=[], tags=["profile"])
    def list(self, request, *args, **kwargs):
        try:
            address_info = Address.objects.filter(
                is_active=True,
                ref_id=request.userinfo["id"],
                ltype=Address.LocationTypes.USER,
                organisation=request.userinfo["organisation"],
            )
            address_data = self.serializer_class(address_info, many=True).data
            return Response(
                {
                    "status": 200,
                    "message": "User address",
                    "data": address_data,
                    "reload": "",
                },
                status=status.HTTP_200_OK,
            )
        except:
            return Return500Error("Internal error, try again after some time.")

    @swagger_wrapper(
        {
            "name": openapi.TYPE_STRING,
            "latitude": openapi.TYPE_STRING,
            "longitude": openapi.TYPE_STRING,
            "contact_person_name": openapi.TYPE_STRING,
            "contact_person_phone": openapi.TYPE_STRING,
            "address_one": openapi.TYPE_STRING,
            "address_two": openapi.TYPE_STRING,
            "city": openapi.TYPE_STRING,
            "state": openapi.TYPE_STRING,
            "country": openapi.TYPE_STRING,
            "zipcode": openapi.TYPE_STRING,
        },
        ["profile"],
    )
    def create(self, request, *args, **kwargs):
        try:
            name = request.data["name"]
            latitude = request.data["latitude"]
            longitude = request.data["longitude"]
            contact_person_name = request.data["contact_person_name"]
            contact_person_phone = request.data["contact_person_phone"]
            address_one = request.data["address_one"]
            address_two = request.data["address_two"]
            city = request.data["city"]
            state = request.data["state"]
            country = request.data["country"]
            zipcode = request.data["zipcode"]

            user = request.userinfo["id"]
            organisation = request.userinfo["organisation"]

            try:
                check_address = Address.objects.filter(
                    name=name,
                    ref_id=user,
                    is_active=True,
                    organisation=organisation,
                    ltype=Address.LocationTypes.USER,
                ).count()
                if check_address > 0:
                    raise Exception("Address with name already exists")
            except:
                return Return400Error("Address with name already exists")

            address_info = Address(
                name=name,
                latitude=latitude,
                longitude=longitude,
                contact_person_name=contact_person_name,
                contact_person_phone=contact_person_phone,
                address_one=address_one,
                address_two=address_two,
                city=city,
                state=state,
                country=country,
                zipcode=zipcode,
                ref_id=user,
                organisation=organisation,
                created_by=user,
                updated_by=user,
                ltype=Address.LocationTypes.USER,
            )
            address_info.save()

            address_data = self.serializer_class(address_info).data
            return Response(
                {
                    "status": 201,
                    "message": "address Created successfully",
                    "data": address_data,
                    "reload": "",
                },
                status=status.HTTP_201_CREATED,
            )

        except:
            return Return500Error("Internal error, try again after sometime.")

    @swagger_auto_schema(manual_parameters=[], tags=["profile"])
    def retrieve(self, request, *args, **kwargs):
        try:
            address_id = kwargs["pk"]
            try:

                address_info = Address.objects.get(
                    id=address_id,
                    is_active=True,
                    ref_id=request.userinfo["id"],
                    organisation=request.userinfo["organisation"],
                    ltype=Address.LocationTypes.USER,
                )
            except:
                return Return404Error("Invalid address Id")
            address_data = self.serializer_class(address_info).data
            return Response(
                {
                    "status": 200,
                    "message": "User address",
                    "data": address_data,
                    "reload": "",
                },
                status=status.HTTP_200_OK,
            )
        except:
            return Return500Error("Internal error, try again after some time.")

    @swagger_wrapper(
        {
            "name": openapi.TYPE_STRING,
            "latitude": openapi.TYPE_STRING,
            "longitude": openapi.TYPE_STRING,
            "contact_person_name": openapi.TYPE_STRING,
            "contact_person_phone": openapi.TYPE_STRING,
            "address_one": openapi.TYPE_STRING,
            "address_two": openapi.TYPE_STRING,
            "city": openapi.TYPE_STRING,
            "state": openapi.TYPE_STRING,
            "country": openapi.TYPE_STRING,
            "zipcode": openapi.TYPE_STRING,
            "status": openapi.TYPE_BOOLEAN,
        },
        ["profile"],
    )
    def update(self, request, *args, **kwargs):
        try:
            address_id = kwargs["pk"]
            organisation = request.userinfo["organisation"]
            user = request.userinfo["id"]

            try:
                address_info = Address.objects.get(
                    id=address_id,
                    is_active=True,
                    ref_id=user,
                    organisation=organisation,
                    ltype=Address.LocationTypes.USER,
                )
            except:
                return Return404Error("Invalid address id sent")

            try:
                if "name" in request.data:
                    check_address = (
                        Address.objects.filter(
                            name=request.data["name"],
                            ref_id=user,
                            is_active=True,
                            organisation=organisation,
                        )
                        .exclude(id=address_id)
                        .count()
                    )
                    if check_address > 0:
                        raise Exception("address already exists")
            except:
                return Return400Error("address with name already exists")

            serializer = self.serializer_class(
                address_info, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                address_info.updated_by = user
                address_info.save()
            else:
                return Return404Error("Invalid address payload sent")

            return Response(
                {
                    "status": 200,
                    "message": "Address updated successfully",
                    "data": serializer.data,
                    "reload": "",
                },
                status=status.HTTP_200_OK,
            )
        except:
            return Return500Error("Internal error, try again after sometime.")

    @swagger_auto_schema(manual_parameters=[], tags=["profile"])
    def destroy(self, request, *args, **kwargs):
        try:
            address_id = kwargs["pk"]
            try:
                address_info = Address.objects.get(
                    id=address_id,
                    is_active=True,
                    ref_id=request.userinfo["id"],
                    ltype=Address.LocationTypes.USER,
                    organisation=request.userinfo["organisation"],
                )
            except:
                return Return404Error("Invalid Address Id")

            address_info.is_active = False
            address_info.deleted_by = request.userinfo["id"]
            address_info.updated_by = request.userinfo["id"]
            address_info.deleted_at = timezone.now()
            address_info.save()

            return Response(
                {
                    "status": 200,
                    "message": "Address deleted successfully",
                    "data": [],
                    "reload": "",
                },
                status=status.HTTP_200_OK,
            )
        except:
            return Return500Error("Internal error, try again after some time.")
