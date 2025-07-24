# core/cache/views.py
from django.core.cache import cache
from rest_framework import generics
from rest_framework.response import Response


class CachedListCreateView(generics.ListCreateAPIView):
    """Generic cached list view"""

    cache_timeout = 60 * 5  # 5 minutes default

    def get_cache_key(self):
        model_name = self.queryset.model.__name__.lower()
        params = self.request.query_params.dict()
        return f"{model_name}_list:{hash(frozenset(params.items()))}"

    def list(self, request, *args, **kwargs):
        cache_key = self.get_cache_key()
        data = cache.get(cache_key)

        print(f"\n🔍 Checking cache for key: {cache_key}")
        print(f"📦 Cache content: {data}")

        if data is not None:
            print("✅ Cache hit - returning cached data")
            return Response(data)  # Changed from self.get_response()

        print("❌ Cache miss - querying database")
        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=60 * 15)
        print(f"💾 Saved to cache with TTL 15min")
        return response

    def perform_create(self, serializer):
        instance = serializer.save()
        print(f"\n🎉 New Event created - ID: {instance.id}")
        # Manually invalidate cache
        self._invalidate_caches()

    def _invalidate_caches(self):
        """Manually clear all related caches"""
        list_keys = cache.keys("*event_list*")
        if list_keys:
            print(f"🧹 Clearing list caches: {list_keys}")
            cache.delete_many(list_keys)
        else:
            print("⚠️ No list caches found to clear")


class CachedRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Generic cached detail view with automatic invalidation"""

    cache_timeout = 60 * 30  # 30 minutes default

    def get_cache_key(self):
        """Generate consistent cache key for this object"""
        model_name = self.get_queryset().model.__name__.lower()
        return f"{model_name}_detail_{self.kwargs['pk']}"

    def retrieve(self, request, *args, **kwargs):
        """Handle GET requests with caching"""
        cache_key = self.get_cache_key()
        data = cache.get(cache_key)

        # Debug print for cache check
        print(f"\n🔍 [RETRIEVE] Checking cache for {cache_key}")
        print(f"📦 Cached data: {data is not None}")

        if data is not None:
            print("✅ Cache hit - returning cached data")
            return Response(data)  # Changed from self.get_response()

        print("❌ Cache miss - querying database")
        response = super().retrieve(request, *args, **kwargs)
        cache.set(cache_key, response.data, self.cache_timeout)
        print(f"💾 Saved to cache (TTL: {self.cache_timeout}s)")
        return response

    def perform_update(self, serializer):
        """Handle cache invalidation on update"""
        instance = self.get_object()
        print(f"\n🔄 [UPDATE] Processing update for {instance}")
        super().perform_update(serializer)

        if hasattr(instance, "invalidate_caches"):
            print("⚡ Triggering cache invalidation from update")
            instance.invalidate_caches()
        else:
            print("⚠️ No invalidate_caches method found")

    def perform_destroy(self, instance):
        """Handle cache invalidation on delete"""
        print(f"\n🗑️ [DELETE] Processing deletion for {instance}")

        # Get cache key BEFORE deletion (while we still have the instance)
        cache_key = self.get_cache_key()
        print(f"🔑 Cache key to invalidate: {cache_key}")

        if hasattr(instance, "invalidate_caches"):
            print("⚡ Triggering cache invalidation from delete")
            instance.invalidate_caches()
        else:
            print("⚠️ No invalidate_caches method found")

        # Manually delete this object's cache as fallback
        if cache.delete(cache_key):
            print("♻️ Manually deleted object cache")
        else:
            print("⚠️ No cache found to delete")

        super().perform_destroy(instance)
        print(f"✅ Successfully deleted {instance}")
