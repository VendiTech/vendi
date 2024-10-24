from django.urls import path

from mspy_vendi.auth.views import DecoratedTokenObtainPairView, DecoratedTokenRefreshView, RegisterView

urlpatterns = [
    path("token/", DecoratedTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", DecoratedTokenRefreshView.as_view(), name="token_refresh"),
    path("register/", RegisterView.as_view(), name="register"),
]
