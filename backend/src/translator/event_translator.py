from github import Github
import os


def get_access_token():
    return os.environ["GITHUB_ACCESS_TOKEN"]

def merge_pull_request(github: Github, repo_name: str, pull_request_id: int):
    repo = github.get_user().get_repo(repo_name)

    desired_pull_request = repo.get_pull(pull_request_id)

    desired_pull_request.merge()


def main():
    token = get_access_token()

    github = Github(token)

    merge_pull_request(github, 'lol-test', 1)


if __name__ == "__main__":
    main()