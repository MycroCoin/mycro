from github import Github
import os


def get_access_token():
    return os.environ["GITHUB_ACCESS_TOKEN"]


def main():
    token = get_access_token()

    github = Github(token)

    for repo in github.get_user().get_repos():
        print(repo.name)


if __name__ == "__main__":
    main()