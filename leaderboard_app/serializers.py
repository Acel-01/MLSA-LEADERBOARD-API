from rest_framework import serializers

from leaderboard_app.models import Submit
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
