"""src URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from common.swagger.documentation import schema_view
from users.urls import urlpatterns as user_urls
from organisation.urls import urlpatterns as organisation_urls
from aws_utils.urls import urlpatterns as aws_urls


urlpatterns = (
    [
        path("admin/", admin.site.urls),
        path(
            "users/docs",
            schema_view.with_ui("swagger", cache_timeout=0),
            name="schema-swagger-ui",
        ),
        path(
            route="users/silk",
            view=include("silk.urls", namespace="silk"),
        ),
    ]
    + user_urls
    + organisation_urls
    + aws_urls
)
urlpatterns += [path("users/prometheus-worke/", include("django_prometheus.urls"))]
