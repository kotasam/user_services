from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


schema_view = get_schema_view(
    openapi.Info(
        title="User API",
        default_version="v1",
        description="For user Micro service",
        terms_of_service="https://worke.io",
        contact=openapi.Contact(email="tech@worke.io"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

# Swagger Wrapper


def swagger_default_wrapper(fields):
    documentation = swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={field: openapi.Schema(type=fields[field]) for field in fields},
        )
    )
    return documentation


def swagger_wrapper(fields, tag=["api"]):
    documentation = swagger_auto_schema(
        tags=tag,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={field: openapi.Schema(type=fields[field]) for field in fields},
        ),
    )
    return documentation


token_param = openapi.Parameter("token", openapi.IN_QUERY, type=openapi.TYPE_STRING)
id_param = openapi.Parameter("id", openapi.IN_QUERY, type=openapi.TYPE_STRING)
staff_id = openapi.Parameter("staff_id", openapi.IN_QUERY, type=openapi.TYPE_STRING)
org_param = openapi.Parameter("org", openapi.IN_QUERY, type=openapi.TYPE_STRING)
org_name = openapi.Parameter("org_name", openapi.IN_QUERY, type=openapi.TYPE_STRING)
# org_param = openapi.Parameter("org", openapi.IN_QUERY, type=openapi.TYPE_STRING)
code_param = openapi.Parameter("code", openapi.IN_QUERY, type=openapi.TYPE_STRING)
email_param = openapi.Parameter("email", openapi.IN_QUERY, type=openapi.TYPE_STRING)
content_type = openapi.Parameter(
    "content_type", openapi.IN_QUERY, type=openapi.TYPE_STRING
)


# For Working hours Create swagger_documentation_decorator :
working_hours_create_api = swagger_auto_schema(
    tags=["working_hours"],
    operation_description="Working Hours Create API",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            field: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "status": openapi.Schema(
                        type="boolean",
                        description="Indicates if there are active slots for Monday",
                    ),
                    "slots": openapi.Schema(
                        type="array",
                        items=openapi.Schema(
                            type="array", items=openapi.Schema(type="string")
                        ),
                    ),
                },
            )
            for field in [
                "MONDAY",
                "TUESDAY",
                "WEDNESDAY",
                "THURSDAY",
                "FRIDAY",
                "SATURDAY",
                "SUNDAY",
            ]
        },
    ),
)

# For Working hours Create swagger_documentation_decorator :
staff_working_hours_create_api = swagger_auto_schema(
    tags=["staff"],
    operation_description="Working Hours Create API",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            field: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "status": openapi.Schema(
                        type="boolean",
                        description="Indicates if there are active slots for Monday",
                    ),
                    "slots": openapi.Schema(
                        type="array",
                        items=openapi.Schema(
                            type="array", items=openapi.Schema(type="string")
                        ),
                    ),
                },
            )
            for field in [
                "MONDAY",
                "TUESDAY",
                "WEDNESDAY",
                "THURSDAY",
                "FRIDAY",
                "SATURDAY",
                "SUNDAY",
            ]
        },
    ),
)
