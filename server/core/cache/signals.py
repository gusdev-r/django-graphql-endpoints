# core/cache/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache


def register_cache_invalidation(model_class):
    """Decorator to register cache invalidation for a model with debug prints"""

    @receiver([post_save, post_delete], sender=model_class)
    def handle_model_changes(sender, instance, **kwargs):
        """Signal handler for cache invalidation"""
        action = (
            "CREATED"
            if kwargs.get("created")
            else "UPDATED" if "created" in kwargs else "DELETED"
        )
        print(
            f"\n🚨 [SIGNAL] {instance.__class__.__name__} {action} - checking invalidation"
        )

        if hasattr(instance, "invalidate_caches"):
            print(f"⚡ Calling invalidate_caches() on {instance}")
            instance.invalidate_caches()

            # Debug: Verify cache was cleared
            if action == "DELETED":
                expected_key = (
                    f"{instance.__class__.__name__.lower()}_detail_{instance.pk}"
                )
                if not cache.has_key(expected_key):
                    print(f"✅ Confirmed cache cleared for {expected_key}")
                else:
                    print(f"❌ Cache still exists for {expected_key}")
        else:
            print(f"⚠️ {instance.__class__.__name__} has no invalidate_caches() method")

    # Debug print to confirm signal registration
    print(f"🔔 Registered cache invalidation for {model_class.__name__}")
    return handle_model_changes
