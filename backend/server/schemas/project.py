import graphene

from graphene_django.types import DjangoObjectType
from graphene import ObjectType

from backend.server.models import Project
import backend.server.utils.github as github
import backend.settings as settings
import asyncio
from backend.server.utils.contract_compiler import ContractCompiler
import backend.server.utils.deploy as deploy


class ProjectException(Exception):
    """Exception for Project related problems"""


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


class CreateProject(graphene.Mutation):
    class Arguments:
        project_name = graphene.String(required=True)
        creator_address = graphene.String(required=True)

    project_address = graphene.String()

    @classmethod
    def _validate_project_name(cls, proposed_project_name):
        github.check_repo_name(proposed_project_name)

        if len(Project.objects.filter(repo_name=proposed_project_name)) > 0:
            raise ProjectException(f'Project with name {proposed_project_name} already exists')

    def mutate(self, info, project_name: str, creator_address: str):
        CreateProject._validate_project_name(proposed_project_name=project_name)
        mycro_project = Project.get_mycro_dao()
        if mycro_project is None:
            raise ProjectException("Could not find mycro dao. Cannot create new project.")

        compiler = ContractCompiler()

        w3 = deploy.get_w3()

        # get the know mycro contract
        contract_interface = compiler.get_contract_interface('mycro.sol', 'MycroCoin')
        mycro_contract = w3.eth.contract(abi=contract_interface['abi'], address=mycro_project.dao_address)

        base_dao_interface = compiler.get_contract_interface('base_dao.sol', 'BaseDao')
        merge_module_interface = compiler.get_contract_interface('merge_module.sol', 'MergeModule')

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        deploy_dao_task: asyncio.Task = asyncio.ensure_future(deploy.deploy_async(base_dao_interface,
                                                                                  project_name,  # name
                                                                                  project_name[:3],  # symbol
                                                                                  18,  # decimals
                                                                                  1000,  # total supply
                                                                                  [creator_address],  # inital addresses
                                                                                  [1000],  # initial balance
                                                                                  private_key=settings.ethereum_private_key()))

        deploy_merge_module_task: asyncio.Task = asyncio.ensure_future(deploy.deploy_async(merge_module_interface,
                                                                                           private_key=settings.ethereum_private_key()))

        # deploy the new DAO and it's merge module
        loop.run_until_complete(asyncio.gather(deploy_dao_task, deploy_merge_module_task))

        # get the results of the async deployment
        w3, dao_contract, dao_address, _ = deploy_dao_task.result()
        _, _, merge_module_address, _ = deploy_merge_module_task.result()

        register_module_task: asyncio.Task = deploy.call_contract_function_async(dao_contract.functions.registerModule,
                                                                                 merge_module_address,
                                                                                 private_key=settings.ethereum_private_key())
        register_dao_task: asyncio.Task = deploy.call_contract_function_async(mycro_contract.functions.registerProject,
                                                                              dao_address,
                                                                              private_key=settings.ethereum_private_key())

        # register the DAO with mycro and register the merge module with the DAO
        loop.run_until_complete(asyncio.gather(register_module_task, register_dao_task))

        loop.close()

        return CreateProject(project_address=dao_address)


class Mutation(graphene.ObjectType):
    create_project = CreateProject.Field()
