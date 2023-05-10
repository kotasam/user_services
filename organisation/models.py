from django.db import models

from common.database.base_model import BaseModel
from src.settings import JWT_SECRET

# Create your models here.
class Organisations(BaseModel):

    slug = models.CharField(max_length=150, blank=False, null=False, unique=True)
    name = models.CharField(max_length=150, blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=100, blank=True, null=True)
    ccode = models.CharField(max_length=10, blank=True, null=True)
    image = models.CharField(max_length=150, blank=True, null=True)
    website = models.CharField(max_length=150, blank=True, null=True)
    address = models.CharField(max_length=150, blank=True, null=True)
    identifier = models.CharField(max_length=150, blank=True, null=True)
    registration_id = models.CharField(max_length=150, blank=True, null=True)
    terms_conditions = models.BooleanField(default=False)

    language = models.CharField(max_length=100, blank=True, null=True)
    instagram_url = models.CharField(max_length=100, blank=True, null=True)
    twitter_url = models.CharField(max_length=100, blank=True, null=True)
    linkedin_url = models.CharField(max_length=100, blank=True, null=True)
    youtube_url = models.CharField(max_length=100, blank=True, null=True)

    api_key = models.CharField(max_length=150, blank=True, null=True)

    def save(self, *args, **kwargs):
        super(Organisations, self).save(*args, **kwargs)
        try:
            print("In save")
            payload = {"name": self.name}
            import jwt

            api_key = jwt.encode(payload=payload, key=JWT_SECRET, algorithm="HS256")
            self.api_key = api_key
            return self
        except Exception as err:
            print("save method exception --->", err)

    def __str__(self):
        return str(self.id)


class GeneralSettings(BaseModel):
    country = models.CharField(max_length=150, blank=False, null=False, default="IND")
    currency = models.CharField(max_length=150, blank=False, null=False, default="INR")
    ccode = models.CharField(max_length=150, blank=False, null=False, default="91")
    timezone = models.CharField(max_length=150, blank=False, null=False, default="IST")
    dateformat = models.CharField(
        max_length=150, blank=False, null=False, default="DD/MM/YYYY"
    )
    timeformat = models.CharField(
        max_length=150, blank=False, null=False, default="HH:MM"
    )
    slot_duration = models.CharField(
        max_length=150, blank=False, null=False, default="30"
    )

    def __str__(self):
        return self.organisation


class Locations(BaseModel):
    class LocationTypes(models.TextChoices):
        USER = "USER", "user"
        ORGANISATION = "ORGANISATION", "organisation"

    name = models.CharField(max_length=100, blank=False, null=False)
    location = models.TextField(blank=True, null=True)
    latitude = models.CharField(max_length=100, blank=True, null=True)
    longitude = models.CharField(max_length=100, blank=True, null=True)
    default = models.BooleanField(default=False)

    contact_person_name = models.CharField(max_length=100, blank=True, null=True)
    contact_person_phone = models.CharField(max_length=100, blank=True, null=True)
    address_one = models.CharField(max_length=100, blank=True, null=True)
    address_two = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    zipcode = models.CharField(max_length=100, blank=True, null=True)

    ltype = models.CharField(
        max_length=100,
        blank=False,
        null=False,
        choices=LocationTypes.choices,
        default=LocationTypes.USER,
    )
    ref_id = models.CharField(max_length=100, blank=False, null=False)

    def __str__(self):
        return str(self.id)


class WorkingHours(BaseModel):
    class WorkingHourTypes(models.TextChoices):
        USER = "USER", "user"
        ORGANISATION = "ORGANISATION", "organisation"
        LOCATIONS = "LOCATIONS", "locations"

    class DayTypes(models.TextChoices):
        MONDAY = "MONDAY", "monday"
        TUESDAY = "TUESDAY", "tuesday"
        WEDNESDAY = "WEDNESDAY", "wednesday"
        THURSDAY = "THURSDAY", "thursday"
        FRIDAY = "FRIDAY", "friday"
        SATURDAY = "SATURDAY", "saturday"
        SUNDAY = "SUNDAY", "sunday"

    days = models.CharField(max_length=100, blank=False, null=False)
    slots = models.JSONField(blank=False, null=False)

    type = models.CharField(
        max_length=100,
        blank=False,
        null=False,
        choices=WorkingHourTypes.choices,
        default=WorkingHourTypes.USER,
    )
    ref_id = models.CharField(max_length=100, blank=False, null=False)

    class Meta:
        unique_together = ["days", "ref_id"]

    def __str__(self):
        return self.days


class RolesPermissions(BaseModel):
    name = models.CharField(max_length=100, blank=False, null=False)
    description = models.CharField(max_length=100, blank=False, null=False)
    permissions = models.JSONField(blank=False, null=False)

    def __str__(self):
        return str(self.id)


class Departments(BaseModel):
    name = models.CharField(max_length=100, blank=False, null=False)
    description = models.CharField(max_length=100, blank=False, null=False)

    def __str__(self):
        return str(self.id)
