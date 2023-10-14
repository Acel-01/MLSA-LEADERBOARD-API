from rest_framework import serializers

from leaderboard_app.models import Submit
from users.models import User
from users.serializers import UserSerializer


class SubmitSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)

    class Meta:
        model = Submit
        exclude = []
        read_only_fields = ["user", "points"]
        extra_kwargs = {
            "pr_link": {
                "error_messages": {
                    "invalid": "Enter a valid URL. e.g https://google.com"
                }
            }
        }


class SubmitErrorSerializer(serializers.Serializer):
    pr_link = serializers.ListField(child=serializers.CharField(max_length=200))


class LeaderboardSerializer(serializers.Serializer):
    member = serializers.CharField(max_length=200)
    rank = serializers.IntegerField()
    score = serializers.FloatField()


class MyRankSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["uuid", "email", "username", "total_points"]
        read_only_fields = ["total_points"]
