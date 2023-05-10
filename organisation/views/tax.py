# from django.utils import timezone
# from rest_framework import viewsets, status
# from rest_framework.response import Response
# from drf_yasg import openapi

# from common.swagger.documentation import swagger_auto_schema, swagger_wrapper
# from organisation.models import TaxRate
# from organisation.serializers import TaxRateSerializer, TaxRateUpdateSerializer
# from organisation.helper import getDeletedTime, getSerializerError
# import logging


# class TaxRateAPI(viewsets.ViewSet):
#     http_method_names = ["get", "post", "put", "delete", "head", "options"]
#     serializer_class = TaxRateSerializer

#     def list(self, request, *args, **kwargs):
#         tax_list = TaxRate.objects.filter(
#             organisation=request.userinfo["organisation"], is_active=True
#         )
#         return Response(
#             {
#                 "status": 200,
#                 "message": "Organisation taxes",
#                 "data": self.serializer_class(tax_list, many=True).data,
#                 "reload": "",
#             },
#             status=status.HTTP_200_OK,
#         )

#     @swagger_wrapper(
#         {
#             "name": openapi.TYPE_STRING,
#             "rate": openapi.TYPE_INTEGER,
#             "default_tax": openapi.TYPE_BOOLEAN,
#             "apply_tax": openapi.TYPE_BOOLEAN,
#         }
#     )
#     def create(self, request, *args, **kwargs):
#         request.data["created_by"] = request.userinfo.get("id")
#         request.data["organisation"] = request.userinfo.get("organisation")
#         serializer = TaxRateSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(
#                 {
#                     "status": 201,
#                     "message": "Tax rate created",
#                     "data": serializer.data,
#                 },
#                 status=status.HTTP_201_CREATED,
#             )
#         return Response(
#             {
#                 "status": 400,
#                 "message": "Invalid info",
#                 "data": getSerializerError(serializer.errors),
#             },
#             status=status.HTTP_400_BAD_REQUEST,
#         )

#     @swagger_wrapper(
#         {
#             "name": openapi.TYPE_STRING,
#             "rate": openapi.TYPE_INTEGER,
#             "default_tax": openapi.TYPE_BOOLEAN,
#             "apply_tax": openapi.TYPE_BOOLEAN,
#         }
#     )
#     def update(self, request, *args, **kwargs):
#         try:
#             tax_rate = TaxRate.objects.get(
#                 id=kwargs.get("pk", None),
#                 organisation=request.data.get("organisation", None),
#                 is_active=True,
#             )
#             request.data["updated_by"] = request.data.get("id")
#             serializer = TaxRateUpdateSerializer(tax_rate, request.data, partial=True)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response(
#                     {
#                         "status": 200,
#                         "message": "Tax updated",
#                         "data": serializer.data,
#                     },
#                     status=status.HTTP_200_OK,
#                 )
#             return Response(
#                 {
#                     "status": 400,
#                     "message": "Invalid data",
#                     "data": getSerializerError(serializer.errors),
#                 },
#                 status=status.HTTP_400_BAD_REQUEST,
#             )
#         except Exception as err:
#             logging.error(f"TaxRateAPI update: {err}", exc_info=True)
#             return Response(
#                 {"status": 400, "message": "Invalid tax", "data": {}},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#     def destroy(self, request, *args, **kwargs):
#         try:
#             tax = TaxRate.objects.get(
#                 id=kwargs.get("pk", None),
#                 organisation=request.data.get("organisation", None),
#                 is_active=True,
#             )
#             tax.is_active = False
#             tax.deleted_by = request.data.get("user_id")
#             tax.deleted_at = getDeletedTime()
#             tax.save()
#             return Response(
#                 {"status": 200, "message": "Tax deleted", "data": []},
#                 status=status.HTTP_200_OK,
#             )
#         except Exception as err:
#             logging.error(f"ZoomtApi destroy: {err}", exc_info=True)
#             return Response(
#                 {"status": 400, "message": "Invalid tax", "data": []},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )
