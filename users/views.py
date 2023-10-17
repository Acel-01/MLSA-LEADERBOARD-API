from djoser import signals
from djoser.conf import settings
from drf_spectacular.utils import OpenApiResponse, extend_schema
from leaderboard.leaderboard import Leaderboard
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

# from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.models import User
from users.serializers import (
    MyTokenObtainPairResponseSerializer,
    MyTokenObtainPairSerializer,
    UserSerializer,
)

leaderboard_name = "mlsa-leaderboard"
redis_mlsa_leaderboard = Leaderboard(leaderboard_name)


@extend_schema(tags=["Authentication"])
class UserCreate(generics.CreateAPIView):
    # throttle_classes = [AnonRateThrottle]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    lookup_field = settings.USER_ID_FIELD

    def get_permissions(self):
        self.permission_classes = settings.PERMISSIONS.user_create
        return super().get_permissions()

    def get_serializer_class(self):
        return settings.SERIALIZERS.user_create_password_retype

    def get_instance(self):
        return self.request.user

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer, *args, **kwargs):
        user = serializer.save(*args, **kwargs)
        signals.user_registered.send(
            sender=self.__class__, user=user, request=self.request
        )


class MyTokenObtainPairView(TokenObtainPairView):
    # throttle_classes = [AnonRateThrottle]
    serializer_class = MyTokenObtainPairSerializer

    @extend_schema(
        tags=["Authentication"],
        responses={
            200: OpenApiResponse(
                response=MyTokenObtainPairResponseSerializer,
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class MyTokenRefreshView(TokenRefreshView):
    # throttle_classes = [AnonRateThrottle]

    @extend_schema(tags=["Authentication"])
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response(serializer.validated_data, status=status.HTTP_200_OK)
