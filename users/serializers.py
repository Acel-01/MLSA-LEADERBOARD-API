from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from mlsa_leaderboard.settings import leaderboard_name, redis_mlsa_leaderboard
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    rank = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["uuid", "email", "username", "total_points", "rank"]
        read_only_fields = ["total_points", "rank"]

    @extend_schema_field(serializers.IntegerField)
    def get_rank(self, obj):
        return None


class UserErrorSerializer(serializers.Serializer):
    email = serializers.ListField(child=serializers.EmailField())
    username = serializers.ListField(child=serializers.CharField(max_length=200))


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        score_and_rank = redis_mlsa_leaderboard.score_and_rank_for_in(
            leaderboard_name=leaderboard_name, member=self.user.username
        )
        user_details = {
            "uuid": str(self.user.uuid),
            "email": self.user.email,
            "username": self.user.username,
            "total_points": self.user.total_points,
            "rank": score_and_rank.get("rank"),
        }
        data["user"] = user_details
        return data


class MyTokenObtainPairResponseSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField()
    user = UserSerializer()
