from django.urls import path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from mspy_vendi.core.swagger.schema_generator import OnlyHttpSchemaGenerator

schema_view = get_schema_view(
    openapi.Info(
        title="Vendi API Schema",
        default_version="v1",
        description="Vendi API Schema",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
    generator_class=OnlyHttpSchemaGenerator,
    authentication_classes=[],
)

urlpatterns = [
    re_path(
        r"swagger(?P<format>\.json|\.yaml)",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    path(
        r"swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path(
        r"redoc/",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc",
    ),
]
