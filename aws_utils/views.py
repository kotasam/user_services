from aws_utils.s3_operations import generate_bucket_key, generate_presigned_url
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
import logging
from common.swagger.documentation import content_type
from drf_yasg.utils import swagger_auto_schema


class PreSignedUrlApi(viewsets.ViewSet):
    http_method_names = ["get", "head"]

    @swagger_auto_schema(
        manual_parameters=[
            content_type,
        ]
    )
    def list(self, request, *args, **kwargs):
        try:
            content_type = self.request.query_params.get("content_type", None)
            if not content_type is None:
                bucket_key = generate_bucket_key(content_type)
                pre_signed_url = generate_presigned_url(bucket_key, content_type)
                return Response(
                    {
                        "status": 200,
                        "message": "Presigned url",
                        "data": {"file_name": bucket_key, "url": pre_signed_url},
                        "reload": "",
                    },
                    status=status.HTTP_200_OK,
                )
        except Exception as err:
            logging.error(f"PreSignedUrlApi create: {err}", exc_info=True)

        return Response(
            {
                "status": 400,
                "message": "Failed to generate presigned url",
                "data": {},
                "reload": "",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
