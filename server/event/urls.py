from django.urls import path
from .views import EventListCreateView, EventDetailView
from django.views.decorators.csrf import csrf_exempt


from django.urls import path
from graphene_django.views import GraphQLView

urlpatterns = [
    path("events/", EventListCreateView.as_view(), name="event-list-create"),
    path("events/<uuid:pk>/", EventDetailView.as_view(), name="event-detail"),
    path("graphql/", csrf_exempt(GraphQLView.as_view(graphiql=True))),
]
