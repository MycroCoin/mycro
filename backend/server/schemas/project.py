import graphene

from graphene_django.types import DjangoObjectType
from graphene import ObjectType

from backend.server.models import Project
from backend.server.tasks import add
from django_celery_beat.models import PeriodicTask, IntervalSchedule


class ProjectType(DjangoObjectType):
    class Meta:
        model = Project


class Query(ObjectType):
    project = graphene.Field(ProjectType,
                             id=graphene.String(),
                             repo_name=graphene.String())
    all_projects = graphene.List(ProjectType)

    def resolve_all_projects(self, info):
        # TODO get rid of this logic because it's just dummy logic
        # This will cause multiple calls to allProjects to fail because we can't create two PeriodicTasks with the same
        # name
        schedule, created = IntervalSchedule.objects.get_or_create(every=1, period=IntervalSchedule.SECONDS, )
        PeriodicTask.objects.create(interval=schedule, name="print 1 constantly",
                                    task='backend.server.tasks.print_stuff')
        return Project.objects.all()

    def resolve_project(self, info, **kwargs):
        repo_name = kwargs.get('repo_name')
        id = kwargs.get('id')

        if id is not None:
            return Project.objects.get(pk=id)

        if repo_name is not None:
            return Project.objects.get(repo_name=repo_name)

        return None


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
