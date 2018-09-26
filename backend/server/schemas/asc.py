import graphene

from graphene_django.types import DjangoObjectType
from graphene import ObjectType

from backend.server.models import ASC, Project
from backend.server.utils.contract_compiler import ContractCompiler
import backend.server.utils.deploy as deploy
import backend.settings as settings


class AscType(DjangoObjectType):
    class Meta:
        model = ASC

    has_executed = graphene.Boolean()
    voters = graphene.List(graphene.String)

    def resolve_has_executed(self: ASC, info):

        asc_contract = deploy.get_asc_contract(self.address)

        return asc_contract.functions.hasExecuted().call()

    def resolve_voters(self: ASC, info):
        dao_contract = deploy.get_dao_contract(self.project.dao_address)

        return dao_contract.functions.getAscVotes(self.address).call()



class Query(ObjectType):
    asc = graphene.Field(AscType,
                         asc_id=graphene.String(),
                         address=graphene.String(),
                         project_id=graphene.String())
    asc_for_project = graphene.List(AscType,
                                    project_address=graphene.String())
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

    def resolve_asc_for_project(self, info, project_address):
        ascs = ASC.objects.filter(project__dao_address=project_address)
        return ascs

    def resolve_get_merge_asc_abi(self, info):
        contract_compiler = ContractCompiler()

        merge_asc_interface = contract_compiler.get_contract_interface("merge_asc.sol", "MergeASC")
        return {'abi': merge_asc_interface['abi'], 'unlinked_binary': merge_asc_interface['bin']}


class CreateMergeASC(graphene.Mutation):
    class Arguments:
        dao_address = graphene.String(required=True)
        rewardee = graphene.String(required=True)
        reward = graphene.Int(required=True)
        pr_id = graphene.Int(required=True)

    asc = graphene.Field(AscType)

    def mutate(self, info, dao_address: str, rewardee: str, reward: int, pr_id: int):
        # validate that we have a DAO with the given address in our DB
        # this may be unnecessary
        project = Project.objects.get(dao_address=dao_address)

        # TODO check that a PR with the given ID exists before executing the rest of this function

        compiler = ContractCompiler()

        w3 = deploy.get_w3()
        base_dao_interface = compiler.get_contract_interface('base_dao.sol', 'BaseDao')
        dao_contract = w3.eth.contract(abi=base_dao_interface['abi'], address=dao_address)

        asc_interface = compiler.get_contract_interface('merge_asc.sol', 'MergeASC')

        # we don't use the async method here because we can't parallelize
        # first the asc has to be deployed to get it's address then the address has to be registered
        # with the base dao
        _, _, asc_address, _ = deploy.deploy(asc_interface, rewardee, reward, pr_id, private_key=settings.ethereum_private_key())

        deploy.call_contract_function(dao_contract.functions.propose, asc_address,
                                      private_key=settings.ethereum_private_key())

        asc = ASC(address=asc_address, project=project, rewardee=rewardee, reward=reward, pr_id=pr_id)
        asc.save()

        return CreateMergeASC(asc=asc)


class Mutation(graphene.ObjectType):
    create_merge_asc = CreateMergeASC.Field()
