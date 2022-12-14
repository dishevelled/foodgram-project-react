from django.contrib import admin
from django.urls import include
from django.urls import re_path as path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("users.urls", namespace="api_users")),
    path("api/", include("api.urls", namespace="api")),
]
