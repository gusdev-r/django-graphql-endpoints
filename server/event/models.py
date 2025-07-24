import uuid
from django.db import models
from core.cache.mixins import AutoInvalidateMixin
from core.cache.signals import register_cache_invalidation
from django.core.cache import cache


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


AutoInvalidateMixin.register_model(Event)

# Only foi views implementation
# def invalidate_caches(self):

#     """Clear all caches related to this event"""
#     print(f"\n🧹 [CACHE] Invalidating caches for Event {self.id}")

#     # 1. Invalidate detail view cache
#     detail_key = f"event_detail_{self.id}"
#     cache.delete(detail_key)
#     print(f"🗑️ Deleted detail cache: {detail_key}")

#     # 2. Invalidate ALL list views
#     list_keys = cache.keys("*event_list*")
#     if list_keys:
#         print(f"🗑️ Deleting {len(list_keys)} list caches")
#         cache.delete_many(list_keys)


# Only foi separated signals implementation
# register_cache_invalidation(Event)
