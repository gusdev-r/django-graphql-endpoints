import graphene
from graphene_django.types import DjangoObjectType
from .models import Event


class EventType(DjangoObjectType):
    class Meta:
        model = Event
        fields = "__all__"


class Query(graphene.ObjectType):
    all_events = graphene.List(EventType)
    event = graphene.Field(EventType, id=graphene.UUID(required=True))

    def resolve_all_events(self, info):
        return Event.objects.all()

    def resolve_event(self, info, id):
        return Event.objects.get(pk=id)


schema = graphene.Schema(query=Query)
