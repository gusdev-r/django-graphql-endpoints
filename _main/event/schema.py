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
    event_by_name = graphene.Field(EventType, name=graphene.String(required=True))

    def resolve_all_events(self, info):
        return Event.objects.all()

    def resolve_event(self, info, id):
        return Event.objects.get(pk=id)

    def resolve_event_by_name(self, info, name):
        return Event.objects.get(name=name)


class CreateEvent(graphene.Mutation):
    class Arguments:
        name = graphene.String()
        description = graphene.String()
        start_date = graphene.DateTime()
        end_date = graphene.DateTime()
        segment = graphene.String()
        location = graphene.String()

    event = graphene.Field(EventType)

    def mutate(self, info, name, description, start_date, end_date, segment, location):
        event = Event.objects.create(
            name=name,
            description=description,
            start_date=start_date,
            end_date=end_date,
            segment=segment,
            location=location,
        )

        return CreateEvent(event=event)


class Mutation(graphene.ObjectType):
    create_event = CreateEvent.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
