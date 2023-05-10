from django.urls import path, include
from rest_framework.routers import DefaultRouter
from aws_utils.views import PreSignedUrlApi


router = DefaultRouter()
router.register("pre_signed_url", PreSignedUrlApi, "pre_signed_url")


urlpatterns = [
    path("users/aws_utils/", include(router.urls)),
]
