from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from common.database.base_model import BaseModel
from organisation.models import RolesPermissions, Departments

# Create your models here.


class User(AbstractBaseUser, BaseModel):
    class UserTypes(models.TextChoices):
        ADMIN = "ADMIN", "admin"
        STAFF = "STAFF", "staff"
        ENDUSER = "ENDUSER", "enduser"
        VISITOR = "VISITOR", "visitor"  # remove
        SUPERADMIN = "SUPERADMIN", "superadmin"

    class SourceTypes(models.TextChoices):
        CONTACT_FORM = "CONTACT_FORM", "contact_form"
        LIVE_CHAT = "LIVE_CHAT", "live_chat"
        MANUAL = "MANUAL", "manual"
        SELF = "SELF", "self"

    fname = models.CharField(max_length=100, blank=True, null=True)
    lname = models.CharField(max_length=100, blank=True, null=True)
    username = models.CharField(max_length=150, blank=False, null=False, unique=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=100, blank=True, null=True)
    ccode = models.CharField(max_length=10, blank=True, null=True)
    image = models.CharField(max_length=150, blank=True, null=True)
    password = models.CharField(max_length=100, blank=True, null=True)
    utype = models.CharField(
        max_length=50, choices=UserTypes.choices, default=UserTypes.ENDUSER
    )
    source = models.CharField(
        max_length=50, choices=SourceTypes.choices, default=SourceTypes.SELF
    )
    external_ids = models.JSONField("External Ids", null=False, default=dict)
    verified = models.BooleanField(default=False)
    initial_setup = models.BooleanField(default=True)

    USERNAME_FIELD = "username"

    class Meta:
        unique_together = [["email", "organisation"]]

    def __str__(self):
        return str(self.id)


class UserProfiles(BaseModel):  # user profile
    user = models.OneToOneField(
        User, related_name="user_info_user", on_delete=models.CASCADE, null=False
    )
    date_of_birth = models.DateField("Date", blank=True, null=True)
    gender = models.CharField(max_length=20, blank=True, null=True)
    age = models.CharField(max_length=20, blank=True, null=True)
    designation = models.CharField(max_length=20, blank=True, null=True)
    specialisation = models.CharField(max_length=20, blank=True, null=True)
    experience = models.CharField(max_length=20, blank=True, null=True)
    qualification = models.CharField(max_length=20, blank=True, null=True)
    description = models.CharField(max_length=20, blank=True, null=True)

    role = models.ForeignKey(
        RolesPermissions,
        related_name="user_role_permission_role_permission",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    department = models.ForeignKey(
        Departments,
        related_name="user_departments",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    def __str__(self):
        return str(self.user.id)


class CustomerProfile(BaseModel):
    user = models.OneToOneField(
        User, related_name="customer_profile_user", on_delete=models.CASCADE, null=False
    )
    date_of_birth = models.DateField("Date", blank=True, null=True)
    gender = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return str(self.user.id)


class UserOTPs(BaseModel):
    class SentTypes(models.TextChoices):
        SMS = "SMS", "sms"
        MAIL = "MAIL", "mail"
        WHATSAPP = "WHATSAPP", "whatsapp"

    class UsedTypes(models.TextChoices):
        LOGIN = "LOGIN", "login"
        ACTIVATE = "ACTIVATE", "activate"
        PASSWORDRESET = "PASSWORDRESET", "passwordreset"

    user = models.CharField(max_length=100, blank=False, null=False)
    otp = models.CharField(max_length=20, blank=True, null=True)
    validity = models.IntegerField(blank=True, null=True, default=10)
    used_for = models.CharField(
        max_length=100, choices=UsedTypes.choices, default=UsedTypes.LOGIN
    )
    sent_to = models.CharField(max_length=100, blank=True, null=True)
    sent_type = models.CharField(
        max_length=100, choices=SentTypes.choices, default=SentTypes.SMS
    )
    validated = models.BooleanField(default=False)
    otp_count = models.IntegerField(default=0)

    def __str__(self):
        return str(self.id)


class UserDepartments(BaseModel):
    user = models.ForeignKey(
        User,
        related_name="user_department_users",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    department = models.ForeignKey(
        Departments,
        related_name="user_department_departments",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    class Meta:
        unique_together = [
            ["user", "department"],
        ]
