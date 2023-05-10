from rest_framework import viewsets, status
from rest_framework.response import Response
from organisation.models import Organisations, Locations
from organisation.serializers import OrganisationSerializer, LocationsSerializer
from users.models import User
from users.serializers import StaffListSerializer
from common.swagger.documentation import (
    swagger_auto_schema,
    org_param,
    id_param,
    org_name,
    staff_id,
)
import logging


class OrganisationIdAPI(viewsets.ViewSet):
    http_method_names = ["get", "head", "options"]

    @swagger_auto_schema(manual_parameters=[org_name], tags=["organisation"])
    def list(self, request, *args, **kwargs):
        try:
            org_name = self.request.query_params.get("org_name")
            if org_name != None:
                org_info = Organisations.objects.get(
                    name=org_name, status=True, is_active=True
                )
                serializer = self.serializer_class(org_info)
                return Response(
                    {
                        "status": 200,
                        "message": "Organisation information",
                        "data": serializer.data,
                        "reload": "",
                    },
                    status=status.HTTP_200_OK,
                )
        except Exception as err:
            logging.error(f"OrganisationIdAPI list: {err}", exc_info=True)
        return Response(
            {"status": 400, "message": "Organisation not found", "data": []},
            status=status.HTTP_400_BAD_REQUEST,
        )


class OrganisationInfoAPI(viewsets.ViewSet):
    http_method_names = ["get", "head", "options"]
    serializer_class = OrganisationSerializer

    @swagger_auto_schema(manual_parameters=[org_param], tags=["organisation"])
    def list(self, request, *args, **kwargs):
        try:
            org_id = self.request.query_params.get("org")
            if org_id != None:
                organisation = Organisations.objects.get(
                    is_active=True, status=True, id=org_id
                )
                serializer = self.serializer_class(organisation)
                return Response(
                    {
                        "status": 200,
                        "message": "Organisation information",
                        "data": serializer.data,
                        "reload": "",
                    },
                    status=status.HTTP_200_OK,
                )
        except Exception as err:
            logging.error(f"OrganisationIdAPI list: {err}", exc_info=True)
        return Response(
            {"status": 400, "message": "Organisation not found", "data": []},
            status=status.HTTP_400_BAD_REQUEST,
        )


class OrganisationLocationAPI(viewsets.ViewSet):
    http_method_names = ["get", "head", "options"]
    serializer_class = LocationsSerializer

    @swagger_auto_schema(manual_parameters=[org_param], tags=["organisation"])
    def list(self, request, *args, **kwargs):
        try:
            org_id = self.request.query_params.get("org")
            if org_id != None:
                locations = Locations.objects.filter(
                    organisation=org_id,
                    status=True,
                    is_active=True,
                    ltype=Locations.LocationTypes.ORGANISATION,
                    ref_id=org_id,
                )
                serializer = self.serializer_class(locations, many=True)
                return Response(
                    {
                        "status": 200,
                        "message": "Organisation locations",
                        "data": serializer.data,
                        "reload": "",
                    },
                    status=status.HTTP_200_OK,
                )
        except Exception as err:
            logging.error(f"OrganisationLocationAPI list: {err}", exc_info=True)
        return Response(
            {"status": 400, "message": "Locations not found", "data": []},
            status=status.HTTP_400_BAD_REQUEST,
        )


class UsersLocationAPI(viewsets.ViewSet):
    http_method_names = ["get", "head", "options"]
    serializer_class = LocationsSerializer

    @swagger_auto_schema(manual_parameters=[org_param, id_param], tags=["organisation"])
    def list(self, request, *args, **kwargs):
        try:
            org_id = self.request.query_params.get("org")
            id_param = self.request.query_params.get("id")
            if org_id != None and id_param != None:
                locations = Locations.objects.filter(
                    organisation=org_id,
                    status=True,
                    is_active=True,
                    ltype=Locations.LocationTypes.USER,
                    ref_id=id_param,
                )
                serializer = self.serializer_class(locations, many=True)
                return Response(
                    {
                        "status": 200,
                        "message": "User locations",
                        "data": serializer.data,
                        "reload": "",
                    },
                    status=status.HTTP_200_OK,
                )
        except Exception as err:
            logging.error(f"UsersLocationAPI list: {err}", exc_info=True)
        return Response(
            {"status": 400, "message": "Locations not found", "data": []},
            status=status.HTTP_400_BAD_REQUEST,
        )


class StaffInfoAPI(viewsets.ViewSet):
    http_method_names = ["get", "head", "options"]
    serializer_class = StaffListSerializer

    @swagger_auto_schema(manual_parameters=[org_param, staff_id], tags=["organisation"])
    def list(self, request, *args, **kwargs):
        try:
            org_id = self.request.query_params.get("org")
            staff_id = self.request.query_params.get("staff_id")
            if org_id != None and staff_id != None:
                staff = User.objects.get(
                    id=staff_id,
                    organisation=org_id,
                    status=True,
                    is_active=True,
                    # utype = User.UserTypes.STAFF
                )
                serializer = self.serializer_class(staff)
                return Response(
                    {
                        "status": 200,
                        "message": "Staff info",
                        "data": serializer.data,
                        "reload": "",
                    },
                    status=status.HTTP_200_OK,
                )
        except Exception as err:
            logging.error(f"StaffInfoAPI list: {err}", exc_info=True)
        return Response(
            {"status": 400, "message": "Staff not found", "data": []},
            status=status.HTTP_400_BAD_REQUEST,
        )
