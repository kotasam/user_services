from rest_framework import serializers
from organisation.models import Locations as Address

from users.models import (
    CustomerProfile,
    User,
    UserDepartments,
    UserProfiles,
    Departments,
)
import logging


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "fname",
            "lname",
            "email",
            "phone_number",
            "ccode",
            "image",
            "utype",
            "organisation",
        ]


class UserGRPCSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = UserSerializer.Meta.fields + ["username", "status"]


class UserProfilesSerializer(serializers.ModelSerializer):

    # role = serializers.SerializerMethodField()
    # departments = serializers.SerializerMethodField()

    # reporter = serializers.SerializerMethodField()

    # def get_role(self, object):  # [TODO]
    #     return "MyRole"

    # def get_departments(self, object):
    #     try:
    #         list_of_departments = UserDepartmentSerializer(
    #             UserDepartments.objects.filter(user=User.objects.get(id=str(object))), many=True
    #         ).data
    #         departments_list = []
    #         for department in list_of_departments:
    #             departments_list.append(str(department["department"]))
    #         return departments_list
    #     except Exception as err:
    #         return []

    # def get_reporter(self, object):  # [TODO]
    #     return "Vivek Sharma"

    class Meta:
        model = UserProfiles
        fields = [
            "date_of_birth",
            "gender",
            "designation",
            "specialisation",
            "age",
            "experience",
            "qualification",
            "description",
            "role",
            "department",
        ]


class CustomerProfilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        fields = ["date_of_birth", "gender"]


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "fname",
            "lname",
            "phone_number",
            "ccode",
            "image",
        ]


class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "fname",
            "lname",
            "email",
            "phone_number",
            "ccode",
            "image",
            "utype",
            "status",
        ]


class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            "id",
            "name",
            "latitude",
            "longitude",
            "contact_person_name",
            "contact_person_phone",
            "address_one",
            "address_two",
            "city",
            "state",
            "country",
            "zipcode",
            "status",
        ]


class UserDepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDepartments
        fields = ["user", "department"]


class DepartmentForStaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departments
        fields = ["id", "name"]


class StaffListSerializer(serializers.ModelSerializer):
    department_info = serializers.SerializerMethodField("get_department_info")

    class Meta:
        model = User
        fields = [
            "id",
            "fname",
            "lname",
            "email",
            "phone_number",
            "ccode",
            "image",
            "utype",
            "status",
            "department_info",
        ]

    def get_department_info(self, obj):
        try:
            user_profile = UserProfiles.objects.get(
                user=str(obj.id), organisation=obj.organisation, is_active=True
            )
            return DepartmentForStaffSerializer(user_profile.department).data
        except Exception as err:
            logging.error(
                f"StaffListSerializer get_department_info: {err}", exc_info=True
            )
            return {}
