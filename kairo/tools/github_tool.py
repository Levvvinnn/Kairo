from __future__ import annotations

from typing import Any

from kairo.tools.base import Tool
from kairo.integrations.github_client import GitHubClient


class GitHubTool(Tool):

    name = "github_repositories"

    description = "Returns user's repositories"

    def __init__(self, client: GitHubClient | None = None) -> None:
        self._client = client

    @property
    def client(self) -> GitHubClient:
        if self._client is None:
            self._client = GitHubClient()
        return self._client

    def execute(self, **kwargs: Any) -> dict[str, Any]:
        try:
            repos = self.client.get_my_repos()
        except Exception as error:
            return {"error": str(error)}

        return {
            "repos": repos
        }
