import graphene

from graphene_django.types import DjangoObjectType
from graphene import relay

from backend.server.models import Project


class ProjectType(DjangoObjectType):
    class Meta:
        model = Project


class Query(object):
    node = relay.Node.Field()

    project = graphene.relay.Node.Field(ProjectType)
    all_projects = graphene.List(ProjectType)

    def resolve_all_projects(self, info, **kwargs):
        return Project.objects.all()

    def resolve_project(self, info, **kwargs):
        id = kwargs.get('id')
        name = kwargs.get('name')

        if id is not None:
            return Project.objects.get(pk=id)

        if name is not None:
            return Project.objects.get(name=name)

        return None
