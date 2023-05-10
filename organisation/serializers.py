from rest_framework import serializers

from organisation.models import (
    GeneralSettings,
    Locations,
    Organisations,
    RolesPermissions,
    WorkingHours,
    Departments,
    # TaxRate,
)
from users.models import UserDepartments, UserProfiles
from users.serializers import UserDepartmentSerializer

from src.settings import JWT_SECRET


class GeneralSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneralSettings
        fields = [
            "country",
            "currency",
            "ccode",
            "timezone",
            "dateformat",
            "timeformat",
            "slot_duration",
        ]


class OrganisationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organisations
        fields = [
            "name",
            "description",
            "slug",
            "email",
            "phone_number",
            "ccode",
            "image",
            "website",
            "address",
            "identifier",
            "registration_id",
            "language",
            "instagram_url",
            "twitter_url",
            "linkedin_url",
            "youtube_url",
        ]

    def create(self, validated_data):
        print("creating")
        obj = Organisations.objects.create(**validated_data)
        obj.save()
        print("created")
        return obj


class OrganisationGRPCSerializer(OrganisationSerializer):
    class Meta:
        model = Organisations


class WorkingHourSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkingHours
        fields = ["days", "slots", "status"]


class RolesPermissionSerializer(serializers.ModelSerializer):

    staff_count = serializers.SerializerMethodField("get_staff_count")

    def get_staff_count(self, object):
        return UserProfiles.objects.filter(
            role=str(object.id), organisation=str(object.organisation), is_active=True
        ).count()

    class Meta:
        model = RolesPermissions
        fields = ["id", "name", "description", "permissions", "status", "staff_count"]


class DepartmentSerializer(serializers.ModelSerializer):

    # users = serializers.SerializerMethodField()

    # def get_users(self, object):
    #     list_of_users = UserDepartmentSerializer(
    #         UserDepartments.objects.filter(department=object), many=True
    #     ).data
    #     users_list = []
    #     for user in list_of_users:
    #         users_list.append(str(user["user"]))
    #     return users_list

    class Meta:
        model = Departments
        fields = ["id", "name", "description", "status"]


class DepartmentListSerializer(serializers.ModelSerializer):
    users_count = serializers.SerializerMethodField("get_users_count")

    class Meta:
        model = Departments
        fields = ["id", "name", "description", "status", "users_count"]

    def get_users_count(self, obj):
        return UserProfiles.objects.filter(
            department=obj, organisation=obj.organisation, status=True, is_active=True
        ).count()


class LocationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Locations
        fields = ["id", "name", "location", "status", "default"]


# class TaxRateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TaxRate
#         fields = [
#             "name",
#             "rate",
#             "default_tax",
#             "apply_tax",
#             "organisation",
#             "created_by",
#             "updated_by",
#         ]


# class TaxRateUpdateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TaxRate
#         fields = [
#             "name",
#             "rate",
#             "default_tax",
#             "apply_tax",
#             "updated_by",
#         ]
