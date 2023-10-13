import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.
class User(AbstractUser):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=255, unique=True, verbose_name=_("username"))
    email = models.EmailField(max_length=255, unique=True, verbose_name=_("email"))
    total_points = models.PositiveIntegerField(
        blank=True,
        null=True,
        default=0,
        help_text=("The amount of points this user has accumulated"),
        verbose_name=_("total points"),
    )

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        return self.username

    class Meta:
        ordering = ["-date_joined"]
