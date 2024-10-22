from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from auth.serializers import (
    TokenObtainPairResponseSerializer,
    TokenRefreshResponseSerializer,
    UserRegistrationSerializer,
    UserResponseRegistrationSerializer,
)


class DecoratedTokenObtainPairView(TokenObtainPairView):
    @swagger_auto_schema(responses={status.HTTP_200_OK: TokenObtainPairResponseSerializer})
    def post(self, request: Request, *args, **kwargs) -> Response:
        return super().post(request, *args, **kwargs)


class DecoratedTokenRefreshView(TokenRefreshView):
    @swagger_auto_schema(responses={status.HTTP_200_OK: TokenRefreshResponseSerializer})
    def post(self, request: Request, *args, **kwargs) -> Response:
        return super().post(request, *args, **kwargs)


class RegisterView(generics.GenericAPIView):
    serializer_class = UserRegistrationSerializer

    @swagger_auto_schema(
        responses={
            status.HTTP_201_CREATED: UserResponseRegistrationSerializer,
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description="Bad Request - User already exists",
                examples={
                    "application/json": {
                        "application/json": {
                            "username": ["A user with that username already exists."],
                        }
                    }
                },
            ),
        }
    )
    def post(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            user_response = UserResponseRegistrationSerializer(user)

            return Response(user_response.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
