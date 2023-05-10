from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.views.authorization.forgot_password import ResetPasswordAPI
from users.views.authorization.forgot_password import ForgotPasswordAPI
from users.views.authorization.login import LoginAPI, RefreshTokenAPI, VerifyUserAPI

from users.views.authorization.register import RegisterAPI
from users.views.authorization.verify_user import ActivateUserAPI, ResendActivationAPI

from users.views.customers.customer_login import CustomerLoginAPI, CustomerOtpVerifyAPI
from users.views.customers.iframe import (
    OrganisationIdAPI,
    OrganisationInfoAPI,
    OrganisationLocationAPI,
    UsersLocationAPI,
    StaffInfoAPI,
)
from users.views.profile.info import TestAPIs, UserInfoAPI
from users.views.profile.user_address import UserAddressAPI
from users.views.staff.staff_information import StaffInformationAPI
from users.views.staff.staff_working_hours import StaffWorkingHoursAPI


auth_router = DefaultRouter()
profile_router = DefaultRouter()
staff_router = DefaultRouter()
customer_router = DefaultRouter()

auth_router.register("register", RegisterAPI, "registartion")
auth_router.register("activate", ActivateUserAPI, "activate user")
auth_router.register("login", LoginAPI, "login")
auth_router.register("forgot-password", ForgotPasswordAPI, "forgot password")
auth_router.register("reset-password", ResetPasswordAPI, "reset password")
# auth_router.register("refresh-token", RefreshTokenAPI, "refresh token") # [TODO]
auth_router.register("resend-activation", ResendActivationAPI, "refresh token")
auth_router.register("verify-user", VerifyUserAPI, "verify user")


profile_router.register("info", UserInfoAPI, "user info")
profile_router.register("test", TestAPIs, "sample test api")
profile_router.register("address", UserAddressAPI, "user info")

staff_router.register("information", StaffInformationAPI, "Staff information")
staff_router.register("working-hours", StaffWorkingHoursAPI, "Staff working hours")

customer_router.register("login", CustomerLoginAPI, "Customer login")
customer_router.register("verify", CustomerOtpVerifyAPI, "Customer login verify")
customer_router.register("organisation", OrganisationIdAPI, "Organisation id")
customer_router.register("organisation-info", OrganisationInfoAPI, "Organisation info")
customer_router.register(
    "organisation-locations", OrganisationLocationAPI, "Organisation locations"
)
customer_router.register("user-locations", UsersLocationAPI, "User locations")
customer_router.register("staff-info", StaffInfoAPI, "Staff info")


urlpatterns = [
    path("users/authorisation/", include(auth_router.urls), name="Authorisation"),
    path("users/profile/", include(profile_router.urls), name="User Profile"),
    path("users/staff/", include(staff_router.urls), name="Staff details"),
    path("users/customer/", include(customer_router.urls), name="Customer details"),
]
