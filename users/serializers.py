from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["uuid", "email", "username", "total_points"]
        read_only_fields = ["total_points"]
