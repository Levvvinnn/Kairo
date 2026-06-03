from kairo.tools.base import Tool
from kairo.integrations.github_client import GitHubClient


class GitHubTool(Tool):

    name = "github_repositories"

    description = "Returns user's repositories"

    def __init__(self):
        self.client = GitHubClient()

    def execute(self, **kwargs):

        repos = self.client.get_my_repos()

        return {
            "repos": repos
        }