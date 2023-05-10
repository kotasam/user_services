from rest_framework import viewsets, status
from rest_framework.response import Response
from drf_yasg import openapi
from organisation.models import WorkingHours

from organisation.serializers import WorkingHourSerializer
from common.swagger.documentation import swagger_auto_schema, working_hours_create_api
from common.helpers.errors_helper import Return400Error, Return500Error


class WorkingHoursAPI(viewsets.ViewSet):
    http_method_names = ["get", "post", "head", "options"]
    serializer_class = WorkingHourSerializer

    @swagger_auto_schema(manual_parameters=[], tags=["working_hours"])
    def list(self, request, *args, **kwargs):
        try:
            try:
                working_hours_info = WorkingHours.objects.filter(
                    ref_id=request.userinfo["organisation"],
                    organisation=request.userinfo["organisation"],
                    type=WorkingHours.WorkingHourTypes.ORGANISATION,
                )
                if working_hours_info.count() < 7:
                    raise Exception("No record found")
            except:
                days = []
                for iterator in WorkingHours.DayTypes:
                    days.append(
                        WorkingHours(
                            days=iterator,
                            slots=[["09:00", "18:00"]],
                            type=WorkingHours.WorkingHourTypes.ORGANISATION,
                            ref_id=request.userinfo["organisation"],
                            organisation=request.userinfo["organisation"],
                        )
                    )
                working_hours_info = WorkingHours.objects.bulk_create(days)

            return_data = self.serializer_class(working_hours_info, many=True).data

            return Response(
                {
                    "status": 200,
                    "message": "Organisation working hours",
                    "data": return_data,
                    "reload": "",
                },
                status=status.HTTP_200_OK,
            )
        except:
            return Return500Error("Internal error, try again after sometime")

    @working_hours_create_api
    def create(self, request, *args, **kwargs):  # [TODO]: slot validations
        try:
            try:
                working_hours_info = WorkingHours.objects.filter(
                    ref_id=request.userinfo["organisation"],
                    organisation=request.userinfo["organisation"],
                    type=WorkingHours.WorkingHourTypes.ORGANISATION,
                )
                if working_hours_info.count() < 7:
                    raise Exception("No record found")

                for wh in working_hours_info:
                    wh.slots = request.data[wh.days]["slots"]
                    wh.status = request.data[wh.days]["status"]

                WorkingHours.objects.bulk_update(
                    working_hours_info, ["slots", "status"]
                )

            except:
                days = []
                for iterator in WorkingHours.DayTypes:
                    days.append(
                        WorkingHours(
                            days=iterator,
                            slots=request.data[iterator]["slots"],
                            status=request.data[iterator]["status"],
                            type=WorkingHours.WorkingHourTypes.ORGANISATION,
                            ref_id=request.userinfo["organisation"],
                            organisation=request.userinfo["organisation"],
                        )
                    )
                working_hours_info = WorkingHours.objects.bulk_create(days)

            return_data = self.serializer_class(working_hours_info, many=True).data

            return Response(
                {
                    "status": 200,
                    "message": "Organisation working hours updated successfully",
                    "data": return_data,
                    "reload": "",
                },
                status=status.HTTP_200_OK,
            )
        except:
            return Return500Error("Internal error, try again after sometime.")
