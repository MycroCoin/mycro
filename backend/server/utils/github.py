from github import Github
import os

def get_github_token():
    return os.environ['GITHUB_TOKEN']


def create_repo(repo_name, organization='mycrocoin'):
    token = get_github_token()
    github = Github(token)

    org = github.get_organization(organization)
    org.create_repo(name=repo_name, auto_init=True)


def merge_pr(repo_name, pr_id, organization='mycrocoin'):
    github = Github(get_github_token())
    org = github.get_organization(organization)
    repo = org.get_repo(repo_name)

    pr = repo.get_pull(pr_id)
    pr.merge()
