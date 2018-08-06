import graphene

from graphene_django.types import DjangoObjectType
from graphene import ObjectType

from backend.server.models import Project
import backend.server.utils.github as github


class ProjectType(DjangoObjectType):
    class Meta:
        model = Project


class Query(ObjectType):
    project = graphene.Field(ProjectType,
                             id=graphene.String(),
                             repo_name=graphene.String())
    all_projects = graphene.List(ProjectType)
    is_project_name_available = graphene.String(proposed_project_name=graphene.String())

    def resolve_all_projects(self, info):
        return Project.objects.all()

    def resolve_project(self, info, **kwargs):
        repo_name = kwargs.get('repo_name')
        id = kwargs.get('id')

        if id is not None:
            return Project.objects.get(pk=id)

        if repo_name is not None:
            return Project.objects.get(repo_name=repo_name)

        return None

    def resolve_is_project_name_available(self, info, proposed_project_name: str):

        try:
            github.check_repo_name(proposed_project_name)

            if len(Project.objects.filter(repo_name=proposed_project_name)) > 0:
                return f'Project with name {proposed_project_name} already exists'
        except ValueError as e:
            return str(e)

class CreateProject(graphene.Mutation):
    class Arguments:
        repo_name = graphene.String(required=True)
        dao_address = graphene.String()

    new_project = graphene.Field(ProjectType)

    def mutate(self, info, repo_name, dao_address):
        p = Project(repo_name=repo_name, dao_address=dao_address)
        p.save()

        return CreateProject(new_project=p)




class Mutation(graphene.ObjectType):
    create_project = CreateProject.Field()
