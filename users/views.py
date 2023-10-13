from djoser import signals
from djoser.conf import settings
from leaderboard.leaderboard import Leaderboard
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

# from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.models import User
from users.serializers import UserSerializer

leaderboard_name = "mlsa-leaderboard"
redis_mlsa_leaderboard = Leaderboard(leaderboard_name)


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
        print(serializer.data)
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

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class MyTokenRefreshView(TokenRefreshView):
    # throttle_classes = [AnonRateThrottle]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class UserDetailView(APIView):
    serializer_class = UserSerializer
    lookup_field = "uuid"

    def get(self, request):
        user_obj = request.user
        serializer = self.serializer_class(user_obj, context={"request": request})

        score_and_rank = redis_mlsa_leaderboard.score_and_rank_for_in(
            leaderboard_name=leaderboard_name, member=request.user.username
        )
        data = serializer.data
        data["rank"] = score_and_rank.get("rank")
        return Response(data=data, status=status.HTTP_200_OK)
