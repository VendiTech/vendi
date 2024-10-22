from django.urls import path

from auth.views import DecoratedTokenObtainPairView, DecoratedTokenRefreshView, RegisterView

urlpatterns = [
    path("api/token/", DecoratedTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", DecoratedTokenRefreshView.as_view(), name="token_refresh"),
    path("api/register/", RegisterView.as_view(), name="register"),
]
