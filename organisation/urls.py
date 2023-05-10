from django.urls import path, include
from rest_framework.routers import DefaultRouter
from organisation.views.departments import DepartmentsAPI

from organisation.views.general_settings import GeneralSettingsAPI
from organisation.views.organisation_information import OrganisationInformationAPI
from organisation.views.organisation_locations import OrganisationLocationsAPI
from organisation.views.roles_permissions import RolesPermissionsAPI
from organisation.views.working_hours import WorkingHoursAPI

# from organisation.views.tax import TaxRateAPI

organisation_router = DefaultRouter()

organisation_router.register("general_settings", GeneralSettingsAPI, "general settings")
organisation_router.register("information", OrganisationInformationAPI, "information")
organisation_router.register("working_hours", WorkingHoursAPI, "working hours")
organisation_router.register(
    "roles_permissions", RolesPermissionsAPI, "roles permissions"
)
organisation_router.register("departments", DepartmentsAPI, "departments")
organisation_router.register("locations", OrganisationLocationsAPI, "locations")
# organisation_router.register("tax_rate", TaxRateAPI, "tax rate")


urlpatterns = [
    path("users/organisation/", include(organisation_router.urls), name="User Profile"),
]
