from rest_framework.response import Response
from rest_framework import status


def Return400Error(message, data=[], reload="", function=""):
    return Response(
        {"status": 400, "message": message, "data": data, "reload": reload},
        status=status.HTTP_400_BAD_REQUEST,
    )


def Return404Error(message, data=[], reload="", function=""):
    return Response(
        {"status": 404, "message": message, "data": data, "reload": reload},
        status=status.HTTP_404_NOT_FOUND,
    )


def Return500Error(
    message,
    data=[],
    reload="",
    function="",
):
    return Response(
        {"status": 500, "message": message, "data": data, "reload": reload},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
