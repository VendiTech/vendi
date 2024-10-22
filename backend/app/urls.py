from django.contrib import admin
from django.urls import include, path

api_urls = [path("auth/", include("auth.urls")), path("", include("core.swagger.urls"))]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(api_urls)),
]
