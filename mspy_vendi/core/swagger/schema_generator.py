from django.conf import settings
from drf_yasg.generators import OpenAPISchemaGenerator


class OnlyHttpSchemaGenerator(OpenAPISchemaGenerator):
    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public)
        schema.schemes = settings.SWAGGER_HOSTS

        return schema
