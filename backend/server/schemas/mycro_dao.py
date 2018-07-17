import graphene
from graphene import ObjectType
from backend.server.models import Project


class Query(ObjectType):
    mycro_dao = graphene.String()

    def resolve_mycro_dao(self, info):
        # There should only be 1
        # use filter to handle the odd event where there's none
        mycro_project = Project.objects.filter(is_mycro_dao=True)

        if len(mycro_project) == 0:
            return None
        elif len(mycro_project) == 1:
            return mycro_project[0].dao_address
        else:
            raise ValueError(f"Found {len(mycro_project)} instances of the mycro project when only expected 1")
