from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from rest_framework.response import Response


class CacheListMixin:
    """Handles list view caching with auto-invalidation"""

    cache_timeout = 60 * 5  # 5 minutes default

    def get_cache_key(self):
        model_name = self.queryset.model.__name__.lower()
        params = {
            k: v
            for k, v in self.request.query_params.dict().items()
            if k not in ["page", "format", "page_size"]
        }
        return f"{model_name}_list:{hash(frozenset(params.items()))}"

    def list(self, request, *args, **kwargs):
        cache_key = self.get_cache_key()
        if (data := cache.get(cache_key)) is not None:
            return Response(data)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=self.cache_timeout)
        return response


class CacheDetailMixin:
    """Handles detail view caching with auto-invalidation"""

    cache_timeout = 60 * 30  # 30 minutes default

    def get_cache_key(self):
        model_name = self.queryset.model.__name__.lower()
        return f"{model_name}_detail_{self.kwargs['pk']}"

    def retrieve(self, request, *args, **kwargs):
        cache_key = self.get_cache_key()
        if (data := cache.get(cache_key)) is not None:
            return Response(data)

        response = super().retrieve(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=self.cache_timeout)
        return response


class AutoInvalidateMixin:
    """Automatically connects signals for cache invalidation"""

    @classmethod
    def register_model(cls, model_class):
        """Call this in models.py to connect signals"""

        @receiver([post_save, post_delete], sender=model_class)
        def invalidate_cache(sender, instance, **kwargs):
            model_name = sender.__name__.lower()

            # Invalidate detail view
            cache.delete(f"{model_name}_detail_{instance.pk}")

            # Invalidate all list views
            keys = cache.keys(f"{model_name}_list:*")
            if keys:
                cache.delete_many(keys)

        return invalidate_cache
