import graphene

from graphene_django.types import DjangoObjectType
from graphene import ObjectType

from backend.server.models import Project


class ProjectType(DjangoObjectType):
    class Meta:
        model = Project


class Query(ObjectType):
    project = graphene.Field(ProjectType,
                             id=graphene.String(),
                             name=graphene.String())
    all_projects = graphene.List(ProjectType)

    def resolve_all_projects(self, info):
        return Project.objects.all()

    def resolve_project(self, info, **kwargs):
        name = kwargs.get('name')
        id = kwargs.get('id')

        if id is not None:
            projects = Project.objects.all()
            return Project.objects.get(pk=id)

        if name is not None:
            projects = Project.objects.all()
            project = Project.objects.get(name=name)
            return Project.objects.get(name=name)

        return None

    def resolve_id(self, info, id):
        return Project.objects.get(pk=id)


class CreateProject(graphene.Mutation):
    class Arguments:
        repo_name = graphene.String(required=True)
        dao_address = graphene.String()
        github_access_token = graphene.String()

    new_project = graphene.Field(ProjectType)

    def mutate(self, info, repo_name, dao_address, github_access_token):
        p = Project(name=repo_name, dao_address=dao_address, github_access_token=github_access_token)
        p.save()

        return CreateProject(new_project=p)


class Mutation(graphene.ObjectType):
    create_project = CreateProject.Field()
