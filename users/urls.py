from django.urls import path

from users.views import (
    MyTokenObtainPairView,
    MyTokenRefreshView,
    UserCreate,
    UserDetailView,
)

urlpatterns = [
    path("create/", UserCreate.as_view(), name="user-create"),
    path("token/", MyTokenObtainPairView.as_view(), name="token-obtain-pair"),
    path("token/refresh/", MyTokenRefreshView.as_view(), name="token-refresh"),
    path("me/", UserDetailView.as_view(), name="logged-in-user"),
]
