"""GitHub repository analysis tools."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from kairo.integrations.github_client import GitHubClient
from kairo.tools.base import Tool


class RepositoryArgument(BaseModel):
    """Shared repository argument validation."""

    repository: str = Field(min_length=1)


class CreateIssueArguments(RepositoryArgument):
    """Arguments required to create a GitHub issue."""

    title: str = Field(min_length=1)
    body: str = Field(default="")


class BaseGitHubRepoTool(Tool):
    """Base class for GitHub tools with lazy client creation."""

    def __init__(self, client: GitHubClient | None = None) -> None:
        self._client = client

    @property
    def client(self) -> GitHubClient:
        if self._client is None:
            self._client = GitHubClient()
        return self._client

    @staticmethod
    def _error(error: Exception) -> dict[str, str]:
        return {"error": str(error)}


class GitHubRepoInfoTool(BaseGitHubRepoTool):
    """Return repository metadata."""

    name = "github_repo_info"
    description = "Returns repository metadata including language, stars, forks, issues, and default branch"

    def execute(self, repository: str) -> dict[str, Any]:
        try:
            arguments = RepositoryArgument(repository=repository)
            return self.client.get_repo_info(arguments.repository)
        except Exception as error:
            return self._error(error)


class GitHubRepoReadmeTool(BaseGitHubRepoTool):
    """Return repository README content."""

    name = "github_repo_readme"
    description = "Returns README content for a GitHub repository"

    def execute(self, repository: str) -> dict[str, Any]:
        try:
            arguments = RepositoryArgument(repository=repository)
            return self.client.get_repo_readme(arguments.repository)
        except Exception as error:
            return self._error(error)


class GitHubRepoIssuesTool(BaseGitHubRepoTool):
    """Return open repository issues."""

    name = "github_repo_issues"
    description = "Returns open GitHub issues with assignees and labels"

    def execute(self, repository: str) -> dict[str, Any]:
        try:
            arguments = RepositoryArgument(repository=repository)
            return self.client.get_repo_issues(arguments.repository)
        except Exception as error:
            return self._error(error)


class GitHubRepoPullRequestsTool(BaseGitHubRepoTool):
    """Return open repository pull requests."""

    name = "github_repo_prs"
    description = "Returns open GitHub pull requests with author and status"

    def execute(self, repository: str) -> dict[str, Any]:
        try:
            arguments = RepositoryArgument(repository=repository)
            return self.client.get_repo_pull_requests(arguments.repository)
        except Exception as error:
            return self._error(error)


class GitHubCreateIssueTool(BaseGitHubRepoTool):
    """Create a GitHub issue."""

    name = "github_create_issue"
    description = "Creates a GitHub issue in a repository"

    def execute(self, repository: str, title: str, body: str = "") -> dict[str, Any]:
        try:
            arguments = CreateIssueArguments(
                repository=repository,
                title=title,
                body=body,
            )
            return self.client.create_issue(
                repository=arguments.repository,
                title=arguments.title,
                body=arguments.body,
            )
        except Exception as error:
            return self._error(error)
