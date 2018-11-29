import graphene

from graphene_django.types import DjangoObjectType
from graphene import ObjectType
from web3 import Web3

from backend.server.models import Project
import backend.server.utils.github as github
import backend.settings as settings
import asyncio
from backend.server.utils.contract_compiler import ContractCompiler
import backend.server.utils.deploy as deploy
from backend.server.schemas.asc import AscType
from backend.server.models import ASC, Wallet, BlockchainState
from typing import List
from backend.server.tasks import create_project


class ProjectException(Exception):
    """Exception for Project related problems"""


class BalanceType(graphene.ObjectType):
    address = graphene.String()
    balance = graphene.Float()  # float because sometimes balances exceed graphene.Int's max value of 2^53


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
    threshold = graphene.Float()
    total_supply = graphene.Float()
    balances = graphene.List(BalanceType)
    pull_requests = graphene.List(PullRequestType)
    url = graphene.String()

    def resolve_ascs(self: Project, info) -> List or None:
        if self is None:
            return None

        return ASC.objects.filter(project__dao_address=self.dao_address)

    def resolve_total_supply(self: Project, info) -> float or None:
        if self is None:
            return None

        base_dao_contract = deploy.get_dao_contract(self.dao_address)

        return base_dao_contract.functions.totalSupply().call()

    def resolve_threshold(self: Project, info) -> float or None:
        if self is None:
            return None

        base_dao_contract = deploy.get_dao_contract(self.dao_address)

        return base_dao_contract.functions.threshold().call()

    def resolve_balances(self: Project, info) -> List[BalanceType] or None:
        if self is None:
            return None

        balances = {}

        base_dao_contract = deploy.get_dao_contract(self.dao_address)

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

        if self.is_mycro_dao:
            return None

        pull_requests = []
        for pull_request in github.get_pull_requests(self.repo_name,
                                                     settings.github_organization(),
                                                     settings.github_token(),
                                                     state='all'):
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

    def resolve_url(self: Project, info) -> str or None:
        if self is None:
            return None

        return f'https://www.github.com/{settings.github_organization()}/{self.repo_name}'


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

    project = graphene.Field(ProjectType)

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

        if not Web3.isAddress(creator_address):
            raise ProjectException('Supplied address is not valid')


        total_supply = 1000
        symbol = project_name[:3]
        decimals = 18
        initial_balances = {creator_address: total_supply}


        # create a row in the a db and a repository in github
        project = Project.objects.create(
            repo_name=project_name,
            last_merge_event_block=0,
            is_mycro_dao=False,
            symbol=symbol,
            decimals=decimals,
            blockchain_state=BlockchainState.PENDING.value,
            initial_balances=initial_balances)

        create_project.delay(project.id)

        return CreateProject(project=project)


class Mutation(graphene.ObjectType):
    create_project = CreateProject.Field()
