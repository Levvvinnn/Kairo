from github import Github

from kairo.config.settings import settings


class GitHubClient:

    def __init__(self):
        self.github = Github(settings.github_token)

    def get_my_repos(self):
        user = self.github.get_user()

        return [
            repo.full_name
            for repo in user.get_repos()
        ]