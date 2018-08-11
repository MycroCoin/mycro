from github import Github
import backend.settings as settings
import re


def create_repo(repo_name, organization):
    check_repo_name(repo_name)

    github = Github(settings.github_token())

    org = github.get_organization(organization)
    org.create_repo(name=repo_name, auto_init=True)


def merge_pr(repo_name, pr_id, organization):
    github = Github(settings.github_token())
    org = github.get_organization(organization)
    repo = org.get_repo(repo_name)

    for pull_request in repo.get_pulls():
        if pull_request.number == pr_id:
            pull_request.merge()


def check_repo_name(repo_name: str):
    # ^ matches beginning, $ matches end. Everything in between must be inthe character class
    regex = '^[a-zA-Z0-9-_.]+$'
    if not re.match(regex, repo_name):
        raise ValueError(f"'{repo_name}' is invalid. It must match the regex '{regex}'")
