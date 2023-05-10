from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.response import Response
from drf_yasg import openapi

from common.swagger.documentation import swagger_auto_schema, swagger_wrapper
from organisation.models import RolesPermissions
from organisation.serializers import RolesPermissionSerializer
from common.helpers.errors_helper import Return400Error, Return500Error, Return404Error


class RolesPermissionsAPI(viewsets.ViewSet):
    http_method_names = ["get", "post", "put", "delete", "head", "options"]
    serializer_class = RolesPermissionSerializer

    statis_roles = ["ADMIN", "MANAGER", "STAFF", "AGENT"]

    @swagger_auto_schema(manual_parameters=[], tags=["roles_permissions"])
    def list(self, request, *args, **kwargs):
        try:
            roles_permissions_info = RolesPermissions.objects.filter(
                organisation=request.userinfo["organisation"], is_active=True
            )

            if roles_permissions_info.count() < 4:
                roles = []
                for iterator in self.statis_roles:
                    roles.append(
                        RolesPermissions(
                            name=iterator,
                            description="",
                            permissions={},
                            organisation=request.userinfo["organisation"],
                        )
                    )
                roles_permissions_info = RolesPermissions.objects.bulk_create(roles)
            roles_permissions_data = self.serializer_class(
                roles_permissions_info, many=True
            ).data
            return Response(
                {
                    "status": 200,
                    "message": "Organisation roles and permissions",
                    "data": roles_permissions_data,
                    "reload": "",
                },
                status=status.HTTP_200_OK,
            )
        except:
            return Return500Error("Internal error, try again after some time.")

    @swagger_wrapper(
        {
            "name": openapi.TYPE_STRING,
            "description": openapi.TYPE_STRING,
            "permissions": openapi.TYPE_OBJECT,
        },
        ["roles_permissions"],
    )
    def create(self, request, *args, **kwargs):
        return Response(
            {
                "status": 200,
                "message": "Currently Inactive",
                "data": [],
                "reload": "",
            },
            status=status.HTTP_200_OK,
        )
        try:
            name = request.data["name"]
            description = request.data["description"]
            permissions = request.data["permissions"]
            organisation = request.userinfo["organisation"]

            try:
                check_roles_permissions = RolesPermissions.objects.filter(
                    name=name, organisation=organisation, is_active=True
                ).count()
                if check_roles_permissions > 0:
                    raise Exception("Role already exists")
            except:
                return Return400Error("Role with name already exists")

            roles_permissions_info = RolesPermissions(
                name=name,
                description=description,
                permissions=permissions,
                organisation=organisation,
                created_by=request.userinfo["id"],
                updated_by=request.userinfo["id"],
            )
            roles_permissions_info.save()

            roles_permissions_data = self.serializer_class(roles_permissions_info).data
            return Response(
                {
                    "status": 200,
                    "message": "Role Created successfully",
                    "data": roles_permissions_data,
                    "reload": "",
                },
                status=status.HTTP_200_OK,
            )

        except:
            return Return500Error("Internal error, try again after sometime.")

    @swagger_wrapper(
        {
            "name": openapi.TYPE_STRING,
            "description": openapi.TYPE_STRING,
            "permissions": openapi.TYPE_OBJECT,
            "status": openapi.TYPE_BOOLEAN,
        },
        ["roles_permissions"],
    )
    def update(self, request, *args, **kwargs):
        return Response(
            {
                "status": 200,
                "message": "Currently Inactive",
                "data": [],
                "reload": "",
            },
            status=status.HTTP_200_OK,
        )
        try:
            role_id = kwargs["pk"]
            organisation = request.userinfo["organisation"]

            try:
                roles_permission_info = RolesPermissions.objects.get(
                    id=role_id, organisation=organisation, is_active=True
                )
            except:
                return Return404Error("Invalid role id sent")

            try:
                if "name" in request.data:
                    check_roles_permissions = (
                        RolesPermissions.objects.filter(
                            name=request.data["name"],
                            organisation=organisation,
                            is_active=True,
                        )
                        .exclude(id=role_id)
                        .count()
                    )
                    if check_roles_permissions > 0:
                        raise Exception("Role already exists")
            except:
                return Return400Error("Role with name already exists")

            serializer = self.serializer_class(
                roles_permission_info, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                roles_permission_info.updated_by = request.userinfo["id"]
                roles_permission_info.save()
            else:
                return Return404Error("Invalid role payload sent")

            return Response(
                {
                    "status": 200,
                    "message": "Role Updated successfully",
                    "data": serializer.data,
                    "reload": "",
                },
                status=status.HTTP_200_OK,
            )
        except:
            return Return500Error("Internal error, try again after sometime.")

    @swagger_auto_schema(manual_parameters=[], tags=["roles_permissions"])
    def destroy(self, request, *args, **kwargs):
        return Response(
            {
                "status": 200,
                "message": "Currently Inactive",
                "data": [],
                "reload": "",
            },
            status=status.HTTP_200_OK,
        )
        try:
            role_id = kwargs["pk"]
            organisation = request.userinfo["organisation"]
            try:
                roles_permission_info = RolesPermissions.objects.get(
                    id=role_id, organisation=organisation, is_active=True
                )
            except:
                return Return404Error("Invalid role id sent")

            roles_permission_info.is_active = False
            roles_permission_info.deleted_by = request.userinfo["id"]
            roles_permission_info.deleted_at = timezone.now()
            roles_permission_info.updated_by = request.userinfo["id"]
            roles_permission_info.save()

            return Response(
                {
                    "status": 200,
                    "message": "Role Deleted successfully",
                    "data": [],
                    "reload": "",
                },
                status=status.HTTP_200_OK,
            )

        except:
            return Return500Error("Internal error, try again after sometime.")
