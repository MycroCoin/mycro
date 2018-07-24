from github import Github
import backend.settings as settings


def create_repo(repo_name, organization='MycroCoin'):
    github = Github(settings.github_token())

    org = github.get_organization(organization)
    org.create_repo(name=repo_name, auto_init=True)


def merge_pr(repo_name, pr_id, organization='MycroCoin'):
    github = Github(settings.github_token())
    org = github.get_organization(organization)
    repo = org.get_repo(repo_name)

    pr = repo.get_pull(pr_id)
    pr.merge()
