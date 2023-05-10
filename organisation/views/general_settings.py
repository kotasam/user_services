from rest_framework.response import Response
from rest_framework import viewsets, status
from drf_yasg import openapi

from common.helpers.errors_helper import Return400Error, Return500Error
from common.swagger.documentation import swagger_wrapper, swagger_auto_schema
from organisation.models import GeneralSettings
from organisation.serializers import GeneralSettingsSerializer


class GeneralSettingsAPI(viewsets.ViewSet):
    http_method_names = ["get", "post", "head", "options"]
    serializer_class = GeneralSettingsSerializer

    @swagger_wrapper(
        {
            "country": openapi.TYPE_STRING,
            "currency": openapi.TYPE_STRING,
            "ccode": openapi.TYPE_STRING,
            "timezone": openapi.TYPE_STRING,
            "dateformat": openapi.TYPE_STRING,
            "timeformat": openapi.TYPE_STRING,
            "slot_duration": openapi.TYPE_STRING,
        },
        ["general_settings"],
    )
    def create(self, request, *args, **kwargs):
        try:
            try:
                general_settings_info = GeneralSettings.objects.get(
                    organisation=request.userinfo["organisation"]
                )
            except:
                general_settings_info = GeneralSettings(
                    organisation=request.userinfo["organisation"]
                )
                general_settings_info.save()

            serializer = self.serializer_class(
                general_settings_info, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
            else:
                return Return400Error("Invalid parameters sent")

            return Response(
                {
                    "status": 200,
                    "message": "Details updated successfully",
                    "data": serializer.data,
                    "reload": "",
                },
                status=status.HTTP_200_OK,
            )
        except:
            return Return500Error("Internal Error, Try again after some time")

    @swagger_auto_schema(manual_parameters=[], tags=["general_settings"])
    def list(self, request, *args, **kwargs):
        try:
            try:
                general_settings_info = GeneralSettings.objects.get(
                    organisation=request.userinfo["organisation"]
                )
            except:
                general_settings_info = GeneralSettings(
                    organisation=request.userinfo["organisation"]
                )
                general_settings_info.save()

            serializer = self.serializer_class(general_settings_info)

            return Response(
                {
                    "status": 200,
                    "message": "Organisation general settings",
                    "data": serializer.data,
                    "reload": "",
                },
                status=status.HTTP_200_OK,
            )
        except:
            return Return500Error("Internal Error, Try again after some time")
