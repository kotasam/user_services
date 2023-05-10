from rest_framework import viewsets, status
from rest_framework.response import Response
from django.utils import timezone
import logging

from drf_yasg import openapi
from organisation.models import Locations

from organisation.serializers import LocationsSerializer
from common.swagger.documentation import swagger_auto_schema, swagger_wrapper
from common.helpers.errors_helper import Return404Error, Return500Error, Return400Error


class OrganisationLocationsAPI(viewsets.ViewSet):
    http_method_names = ["get", "post", "put", "delete", "head", "options"]
    serializer_class = LocationsSerializer

    @swagger_auto_schema(manual_parameters=[], tags=["locations"])
    def list(self, request, *args, **kwargs):
        try:
            locations_info = Locations.objects.filter(
                organisation=request.userinfo["organisation"],
                is_active=True,
                ltype=Locations.LocationTypes.ORGANISATION,
                ref_id=request.userinfo["organisation"],
            )
            locations_data = self.serializer_class(locations_info, many=True).data
            return Response(
                {
                    "status": 200,
                    "message": "Organisation locations",
                    "data": locations_data,
                    "reload": "",
                },
                status=status.HTTP_200_OK,
            )
        except Exception as err:
            logging.error(f"OrganisationLocationsAPI list: {err}", exc_info=True)
            return Return500Error("Internal error, try again after some time.")

    @swagger_wrapper(
        {"name": openapi.TYPE_STRING, "location": openapi.TYPE_STRING},
        ["locations"],
    )
    def create(self, request, *args, **kwargs):
        try:
            name = request.data["name"]
            location = request.data["location"]
            user = request.userinfo["id"]
            organisation = request.userinfo["organisation"]

            try:
                check_locations = Locations.objects.filter(
                    name=name,
                    ref_id=organisation,
                    organisation=organisation,
                    ltype=Locations.LocationTypes.ORGANISATION,
                    is_active=True,
                ).count()
                if check_locations > 0:
                    raise Exception("Location with name already exists")
            except:
                return Return400Error("Location with name already exists")

            location_info = Locations(
                name=name,
                location=location,
                ref_id=organisation,
                organisation=organisation,
                created_by=user,
                updated_by=user,
                ltype=Locations.LocationTypes.ORGANISATION,
            )
            location_info.save()

            location_data = self.serializer_class(location_info).data
            return Response(
                {
                    "status": 201,
                    "message": "location Created successfully",
                    "data": location_data,
                    "reload": "",
                },
                status=status.HTTP_201_CREATED,
            )

        except:
            return Return500Error("Internal error, try again after sometime.")

    @swagger_auto_schema(manual_parameters=[], tags=["locations"])
    def retrieve(self, request, *args, **kwargs):
        try:
            location_id = kwargs["pk"]
            try:

                locations_info = Locations.objects.get(
                    id=location_id,
                    is_active=True,
                    ref_id=request.userinfo["organisation"],
                    organisation=request.userinfo["organisation"],
                    ltype=Locations.LocationTypes.ORGANISATION,
                )
            except:
                return Return404Error("Invalid Location Id")
            locations_data = self.serializer_class(locations_info).data
            return Response(
                {
                    "status": 200,
                    "message": "Organisation locations",
                    "data": locations_data,
                    "reload": "",
                },
                status=status.HTTP_200_OK,
            )
        except:
            return Return500Error("Internal error, try again after some time.")

    @swagger_wrapper(
        {
            "name": openapi.TYPE_STRING,
            "location": openapi.TYPE_STRING,
            "default": openapi.TYPE_BOOLEAN,
            "status": openapi.TYPE_BOOLEAN,
        },
        ["locations"],
    )
    def update(self, request, *args, **kwargs):
        try:
            location_id = kwargs["pk"]
            organisation = request.userinfo["organisation"]

            try:
                location_info = Locations.objects.get(
                    id=location_id,
                    organisation=organisation,
                    ref_id=organisation,
                    is_active=True,
                    ltype=Locations.LocationTypes.ORGANISATION,
                )
            except:
                return Return404Error("Invalid location id sent")

            try:
                pass
                if (
                    "default" in request.data
                    and location_info.default != request.data.get("default")
                ):
                    my_queryset = Locations.objects.filter(
                        organisation=organisation,
                        is_active=True,
                        ltype=Locations.LocationTypes.ORGANISATION,
                    )
                    my_queryset.update(default=False)
            except:
                return Return404Error("Failed to make it default")

            try:
                if "name" in request.data:
                    check_locations = (
                        Locations.objects.filter(
                            name=request.data["name"],
                            organisation=organisation,
                            is_active=True,
                            ref_id=request.userinfo["organisation"],
                        )
                        .exclude(id=location_id)
                        .count()
                    )
                    if check_locations > 0:
                        raise Exception("location already exists")
            except:
                return Return400Error("location with name already exists")

            serializer = self.serializer_class(
                location_info, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                location_info.updated_by = request.userinfo["id"]
                location_info.save()
            else:
                return Return404Error("Invalid location payload sent")

            return Response(
                {
                    "status": 200,
                    "message": "Location Updated successfully",
                    "data": serializer.data,
                    "reload": "",
                },
                status=status.HTTP_200_OK,
            )
        except:
            return Return500Error("Internal error, try again after sometime.")

    @swagger_auto_schema(manual_parameters=[], tags=["locations"])
    def destroy(self, request, *args, **kwargs):
        try:
            location_id = kwargs["pk"]
            try:
                locations_info = Locations.objects.get(
                    id=location_id,
                    is_active=True,
                    ref_id=request.userinfo["organisation"],
                    organisation=request.userinfo["organisation"],
                    ltype=Locations.LocationTypes.ORGANISATION,
                )
            except:
                return Return404Error("Invalid Location Id")

            locations_info.is_active = False
            locations_info.deleted_by = request.userinfo["id"]
            locations_info.updated_by = request.userinfo["id"]
            locations_info.deleted_at = timezone.now()
            locations_info.save()

            return Response(
                {
                    "status": 200,
                    "message": "Location deleted successfully",
                    "data": [],
                    "reload": "",
                },
                status=status.HTTP_200_OK,
            )
        except:
            return Return500Error("Internal error, try again after some time.")
