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
                             repo_name=graphene.String())
    all_projects = graphene.List(ProjectType)

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


class CreateProject(graphene.Mutation):
    class Arguments:
        repo_name = graphene.String(required=True)
        dao_address = graphene.String()

    new_project = graphene.Field(ProjectType)

    def mutate(self, info, repo_name, dao_address):
        p = Project(repo_name=repo_name, dao_address=dao_address)
        p.save()

        return CreateProject(new_project=p)


class CreateRegisterDao(graphene.Mutation):
    class Arguments:
        name = graphene.String()

    result = graphene.String()

    def mutate(self, info, name):
        from backend.urls import w3, mycro_instance
        from backend.server.utils.utils import deploy_contract
        from backend.server.utils.contract_compiler import ContractCompiler

        compiler = ContractCompiler()

        dao_interface = compiler.get_contract_interface("base_dao.sol", "BaseDao")
        merge_module_interface = compiler.get_contract_interface("merge_module.sol", "MergeModule")

        _, dao_address, dao_instance = deploy_contract(w3, dao_interface, 'lol', name, 18, 100,
                                                       [w3.eth.accounts[0]], [100])
        merge_contract, merge_address, merge_instance = deploy_contract(w3, merge_module_interface)

        w3.eth.waitForTransactionReceipt(dao_instance.registerModule(merge_address, transact={'from': w3.eth.accounts[0]}))
        w3.eth.waitForTransactionReceipt(mycro_instance.registerProject(dao_address, transact={'from': w3.eth.accounts[0]}))

        return CreateRegisterDao(result=dao_address)


class CreateApproveASC(graphene.Mutation):
    class Arguments:
        dao_address = graphene.String(required=True)
        pr_id = graphene.Int(required=True)

    result = graphene.String()

    def mutate(self, info, dao_address, pr_id):
        from backend.urls import w3, mycro_instance
        from backend.server.utils.utils import deploy_contract
        from backend.server.utils.contract_compiler import ContractCompiler
        from web3.contract import ConciseContract

        compiler = ContractCompiler()

        dao_interface = compiler.get_contract_interface("base_dao.sol", "BaseDao")
        asc_interface = compiler.get_contract_interface("merge_asc.sol", "MergeASC")

        dao_instance = w3.eth.contract(abi=dao_interface['abi'], address=dao_address,
                                       ContractFactoryClass=ConciseContract)
        _, asc_address, asc_instance = deploy_contract(w3, asc_interface, pr_id)

        w3.eth.waitForTransactionReceipt(dao_instance.propose(asc_address, transact={'from': w3.eth.accounts[0]}))
        w3.eth.waitForTransactionReceipt(mycro_instance.registerProject(dao_address, transact={'from': w3.eth.accounts[0]}))

        w3.eth.waitForTransactionReceipt(dao_instance.vote(asc_address, transact={'from': w3.eth.accounts[0]}))

        return CreateApproveASC(result=asc_address)


class Mutation(graphene.ObjectType):
    create_project = CreateProject.Field()
    create_approve_asc = CreateApproveASC.Field()
    create_register_dao = CreateRegisterDao.Field()
