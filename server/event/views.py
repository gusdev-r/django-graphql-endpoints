from rest_framework import generics
from .models import Event
from .serializers import EventSerializer

from core.cache.views import CachedListCreateView, CachedRetrieveUpdateDestroyView
from core.cache.mixins import (
    CacheDetailMixin,
    CacheListMixin,
)


class EventListCreateView(CacheListMixin, generics.ListCreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer


class EventDetailView(CacheDetailMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
