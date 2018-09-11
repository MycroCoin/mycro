import github
import github.PaginatedList
import backend.settings as settings
import re


def create_repo(repo_name, organization):
    check_repo_name(repo_name)

    gh = github.Github(settings.github_token())

    org = gh.get_organization(organization)
    org.create_repo(name=repo_name, auto_init=True)


def get_pull_requests(repo_name: str, organization: str, token: str,
                      **kwargs) -> github.PaginatedList:
    """
    Gets the pull requests of a repository
    :param repo_name: the name of the repo
    :param organization: the organization that the repository belongs to
    :param token: the token used to authenticate with github
    :param kwargs: passed directly to the get repo call: https://bit.ly/2Mlyklc
    :return: list of pull requests
    """
    gh = github.Github(token)
    org = gh.get_organization(organization)
    repo = org.get_repo(repo_name)

    return repo.get_pulls(**kwargs)


def merge_pr(repo_name: str, pr_id: int, organization: str):
    for pull_request in get_pull_requests(repo_name=repo_name,
                                          organization=organization,
                                          token=settings.github_token()):
        if pull_request.number == pr_id:
            pull_request.merge()


def check_repo_name(repo_name: str):
    # ^ matches beginning, $ matches end. Everything in between must be inthe character class
    regex = '^[a-zA-Z0-9-_.]+$'
    if not re.match(regex, repo_name):
        raise ValueError(
            f"'{repo_name}' is invalid. It must match the regex '{regex}'")


def list_repos(organization_name: str, github_token: str):
    gh = github.Github(github_token)
    org = gh.get_organization(organization_name)

    return org.get_repos()
