from django.contrib import admin
from django.urls import include, path

api_urls = [
    path("auth/", include("mspy_vendi.auth.urls")),
    path("", include("mspy_vendi.core.swagger.urls")),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(api_urls)),
]
