import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from users.models import User


# Create your models here.
class Submit(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="submits", verbose_name=_("user")
    )
    pr_link = models.URLField(
        blank=False,
        error_messages={"invalid": "Enter a valid URL. e.g https://google.com"},
        null=False,
        max_length=2000,
        verbose_name=_("pr link"),
    )
    points = models.PositiveIntegerField(
        blank=False,
        null=False,
        help_text=("The points value for the submitted PR"),
        verbose_name=_("points"),
    )
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date_created"]
        verbose_name_plural = "Submissions"

    def __str__(self):
        return f"{self.user.username} {self.points}"
