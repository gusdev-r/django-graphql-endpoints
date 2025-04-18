import uuid
from django.db import models


class SocialNet(models.TextChoices):
    INSTAGRAM = "instagram", "Instagram"
    LINKEDIN = "linkedin", "Linkedin"


class Link(models.Model):
    type = models.CharField(max_length=20, choices=SocialNet.choices)
    link = models.URLField()
    event = models.ForeignKey(
        "Event", related_name="related_links", on_delete=models.CASCADE
    )


class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=120)
    description = models.CharField(max_length=320)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=100, default="gusdev")

    segment = models.CharField(
        max_length=100, blank=True, default="Software Development"
    )
    location = models.CharField(max_length=200, blank=True, default="Brasil")

    def __str__(self):
        return f"{self.name} in {self.location}"
