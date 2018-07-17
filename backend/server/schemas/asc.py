import graphene

from graphene_django.types import DjangoObjectType
from graphene import ObjectType

from backend.server.models import ASC, Project
from backend.server.utils.contract_compiler import ContractCompiler


class AscType(DjangoObjectType):
    class Meta:
        model = ASC


class Query(ObjectType):
    asc = graphene.Field(AscType,
                         asc_id=graphene.String(),
                         address=graphene.String(),
                         project_id=graphene.String())
    asc_for_project = graphene.List(AscType,
                                    project_id=graphene.String())
    all_ASCs = graphene.List(AscType)

    get_merge_asc_abi = graphene.JSONString()

    def resolve_all_ASCs(self, info):
        all_ascs = ASC.objects.all()
        return all_ascs

    def resolve_asc(self, info, **kwargs):
        asc_id = kwargs.get('asc_id')
        address = kwargs.get('address')

        if asc_id is not None:
            return ASC.objects.get(pk=asc_id)

        if address is not None:
            return ASC.objects.get(address=address)

        raise Exception("Uhoh, something went horribly wrong. This should never be raised. Graphql won't allow neither "
                        "of these parameters to exist.")

    def resolve_asc_for_project(self, info, project_id):
        ascs = ASC.objects.filter(project__pk=project_id)
        return ascs

    def resolve_get_merge_asc_abi(self, info):
        contract_compiler = ContractCompiler()

        merge_asc_interface = contract_compiler.get_contract_interface("merge_asc.sol", "MergeASC")
        return { 'abi': merge_asc_interface['abi'], 'unlinked_binary': merge_asc_interface['bin']}


class CreateASC(graphene.Mutation):
    class Arguments:
        address = graphene.String(required=True)
        project_id = graphene.String(required=True)

    new_asc = graphene.Field(AscType)

    def mutate(self, info, address, project_id):
        project = Project.objects.get(pk=project_id)
        asc = ASC(address=address, project=project)
        asc.save()

        return CreateASC(new_asc=asc)


class Mutation(graphene.ObjectType):
    create_asc = CreateASC.Field()
