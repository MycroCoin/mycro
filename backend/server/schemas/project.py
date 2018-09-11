import graphene

from graphene_django.types import DjangoObjectType
from graphene import ObjectType

from backend.server.models import Project
import backend.server.utils.github as github
import backend.settings as settings
import asyncio
from backend.server.utils.contract_compiler import ContractCompiler
import backend.server.utils.deploy as deploy
from backend.server.schemas.asc import AscType
from backend.server.models import ASC
from typing import List


class ProjectException(Exception):
    """Exception for Project related problems"""


def _get_dao_contract(dao_address):
    compiler = ContractCompiler()
    w3 = deploy.get_w3()

    base_dao_interface = compiler.get_contract_interface('base_dao.sol',
                                                         'BaseDao')
    base_dao_contract = w3.eth.contract(abi=base_dao_interface['abi'],
                                        address=dao_address)

    return base_dao_contract


class BalanceType(graphene.ObjectType):
    address = graphene.String()
    balance = graphene.Int()


class PullRequestType(graphene.ObjectType):
    additions = graphene.Int()
    # assignee = github.NamedUser
    # assignees = List[github.NamedUser]
    # base = github.PullRequestPart
    body = graphene.String()
    changed_files = graphene.Int()
    closed_at = graphene.DateTime()
    comments = graphene.Int()
    comments_url = graphene.String()
    commits = graphene.Int()
    commits_url = graphene.String()
    created_at = graphene.DateTime()
    deletions = graphene.Int()
    diff_url = graphene.String()
    # head = List[github.PullRequestPart]
    html_url = graphene.String()
    id = graphene.Int()
    issue_url = graphene.String()
    # labels = List[github.Label]
    merge_commit_sha = graphene.String()
    mergeable = graphene.Boolean()
    mergeable_state = graphene.String()
    merged = graphene.Boolean()
    merged_at = graphene.DateTime()
    # merged_by = github.NamedUser
    # milestone = github.Milestone
    number = graphene.Int()
    patch_url = graphene.String()
    review_comment_url = graphene.String()
    review_comments = graphene.String()
    review_comments_url = graphene.String()
    state = graphene.String()
    title = graphene.String()
    updated_at = graphene.String()
    url = graphene.String()
    # user = github.NamedUser


class ProjectType(DjangoObjectType):
    class Meta:
        model = Project

    ascs = graphene.List(AscType)
    threshold = graphene.Int()
    balances = graphene.List(BalanceType)
    pull_requests = graphene.List(PullRequestType)

    def resolve_ascs(self: Project, info) -> List or None:
        if self is None:
            return None

        return ASC.objects.filter(project__dao_address=self.dao_address)

    def resolve_threshold(self: Project, info) -> int or None:
        if self is None:
            return None

        base_dao_contract = _get_dao_contract(self.dao_address)

        return base_dao_contract.functions.threshold().call()

    def resolve_balances(self: Project, info) -> List[BalanceType] or None:
        if self is None:
            return None

        balances = {}

        base_dao_contract = _get_dao_contract(self.dao_address)

        transactors = base_dao_contract.functions.getTransactors().call()

        for transactor in transactors:
            balances[transactor] = base_dao_contract.functions.balanceOf(
                transactor).call()

        return [BalanceType(address=transactor, balance=balance) for
                transactor, balance in balances.items()]

    def resolve_pull_requests(self: Project, info) -> List[
                                                          PullRequestType] or None:
        if self is None:
            return None

        pull_requests = []
        for pull_request in github.get_pull_requests(self.repo_name,
                                                     settings.github_organization(),
                                                     settings.github_token()):
            pull_requests.append(
                PullRequestType(
                    additions=pull_request.additions,
                    body=pull_request.body,
                    changed_files=pull_request.changed_files,
                    closed_at=pull_request.closed_at,
                    comments=pull_request.comments,
                    comments_url=pull_request.comments_url,
                    commits=pull_request.commits,
                    commits_url=pull_request.commits_url,
                    created_at=pull_request.created_at,
                    deletions=pull_request.deletions,
                    diff_url=pull_request.diff_url,
                    html_url=pull_request.html_url,
                    id=pull_request.id,
                    issue_url=pull_request.issue_url,
                    merge_commit_sha=pull_request.merge_commit_sha,
                    mergeable=pull_request.mergeable,
                    mergeable_state=pull_request.mergeable_state,
                    merged=pull_request.merged,
                    merged_at=pull_request.merged_at,
                    number=pull_request.number,
                    patch_url=pull_request.patch_url,
                    review_comment_url=pull_request.review_comment_url,
                    review_comments=pull_request.review_comments,
                    review_comments_url=pull_request.review_comments_url,
                    state=pull_request.state,
                    title=pull_request.title,
                    updated_at=pull_request.updated_at,
                    url=pull_request.url
                )
            )

        return pull_requests


class Query(ObjectType):
    project = graphene.Field(ProjectType,
                             dao_address=graphene.String())
    all_projects = graphene.List(ProjectType)
    is_project_name_available = graphene.String(
        proposed_project_name=graphene.String())

    def resolve_all_projects(self, info):
        return Project.objects.all()

    def resolve_project(self, info, dao_address):
        return Project.objects.get(dao_address=dao_address)


class CreateProject(graphene.Mutation):
    class Arguments:
        project_name = graphene.String(required=True)
        creator_address = graphene.String(required=True)

    project_address = graphene.String()

    @classmethod
    def _validate_project_name(cls, proposed_project_name):
        github.check_repo_name(proposed_project_name)

        if len(Project.objects.filter(repo_name=proposed_project_name)) > 0:
            raise ProjectException(
                f'Project with name {proposed_project_name} already exists')

    def mutate(self, info, project_name: str, creator_address: str):
        CreateProject._validate_project_name(proposed_project_name=project_name)
        mycro_project = Project.get_mycro_dao()
        if mycro_project is None:
            raise ProjectException(
                "Could not find mycro dao. Cannot create new project.")

        compiler = ContractCompiler()

        w3 = deploy.get_w3()

        # get the know mycro contract
        contract_interface = compiler.get_contract_interface('mycro.sol',
                                                             'MycroCoin')
        mycro_contract = w3.eth.contract(abi=contract_interface['abi'],
                                         address=mycro_project.dao_address)

        base_dao_interface = compiler.get_contract_interface('base_dao.sol',
                                                             'BaseDao')
        merge_module_interface = compiler.get_contract_interface(
            'merge_module.sol', 'MergeModule')

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        symbol = project_name[:3]
        decimals = 18  # todo acccept this as a parameter
        total_supply = 1000  # todo accept this as a parameter
        deploy_dao_task: asyncio.Task = asyncio.ensure_future(
            deploy.deploy_async(base_dao_interface,
                                symbol,
                                project_name,
                                decimals,
                                total_supply,
                                [creator_address],  # inital addresses
                                [total_supply],  # initial balance
                                private_key=settings.ethereum_private_key()))

        deploy_merge_module_task: asyncio.Task = asyncio.ensure_future(
            deploy.deploy_async(merge_module_interface,
                                private_key=settings.ethereum_private_key()))

        # deploy the new DAO and it's merge module
        loop.run_until_complete(
            asyncio.gather(deploy_dao_task, deploy_merge_module_task))

        # get the results of the async deployment
        w3, dao_contract, dao_address, _ = deploy_dao_task.result()
        _, _, merge_module_address, _ = deploy_merge_module_task.result()

        register_module_task: asyncio.Task = deploy.call_contract_function_async(
            dao_contract.functions.registerModule,
            merge_module_address,
            private_key=settings.ethereum_private_key())
        register_dao_task: asyncio.Task = deploy.call_contract_function_async(
            mycro_contract.functions.registerProject,
            dao_address,
            private_key=settings.ethereum_private_key())

        # register the DAO with mycro and register the merge module with the DAO
        loop.run_until_complete(
            asyncio.gather(register_module_task, register_dao_task))

        loop.close()

        # create a row in the a db and a repository in github
        Project.objects.create(
            repo_name=project_name,
            dao_address=dao_address,
            merge_module_address=merge_module_address,
            last_merge_event_block=0,
            is_mycro_dao=False,
            symbol=symbol,
            decimals=decimals)
        github.create_repo(repo_name=project_name,
                           organization=settings.github_organization())

        return CreateProject(project_address=dao_address)


class Mutation(graphene.ObjectType):
    create_project = CreateProject.Field()
