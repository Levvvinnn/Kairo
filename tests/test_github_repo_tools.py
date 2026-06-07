from __future__ import annotations

from typing import Any

from kairo.tools.github_repo_tools import (
    GitHubCreateIssueTool,
    GitHubRepoInfoTool,
    GitHubRepoIssuesTool,
    GitHubRepoPullRequestsTool,
    GitHubRepoReadmeTool,
)


class FakeGitHubClient:
    def get_repo_info(self, repository: str) -> dict[str, Any]:
        return {
            "name": f"levin/{repository}",
            "description": "Focus app",
            "language": "Python",
            "stars": 10,
            "forks": 2,
            "open_issues": 3,
            "default_branch": "main",
        }

    def get_repo_readme(self, repository: str) -> dict[str, str]:
        return {
            "repository": repository,
            "path": "README.md",
            "content": "# FocusDen",
        }

    def get_repo_issues(self, repository: str) -> dict[str, Any]:
        return {
            "repository": repository,
            "open_issues": [
                {
                    "number": 1,
                    "title": "Improve onboarding",
                    "assignees": ["levin"],
                    "labels": ["enhancement"],
                }
            ],
        }

    def get_repo_pull_requests(self, repository: str) -> dict[str, Any]:
        return {
            "repository": repository,
            "open_pull_requests": [
                {
                    "number": 4,
                    "title": "Add settings page",
                    "author": "levin",
                    "status": "open",
                }
            ],
        }

    def create_issue(self, repository: str, title: str, body: str) -> dict[str, Any]:
        return {
            "repository": repository,
            "number": 7,
            "title": title,
            "url": "https://github.com/levin/FocusDen/issues/7",
            "state": "open",
            "body": body,
        }


def test_github_repo_info_tool_returns_repository_metadata() -> None:
    tool = GitHubRepoInfoTool(client=FakeGitHubClient())  # type: ignore[arg-type]

    result = tool.execute(repository="FocusDen")

    assert result["name"] == "levin/FocusDen"
    assert result["language"] == "Python"
    assert result["default_branch"] == "main"


def test_github_repo_readme_tool_returns_readme_content() -> None:
    tool = GitHubRepoReadmeTool(client=FakeGitHubClient())  # type: ignore[arg-type]

    result = tool.execute(repository="FocusDen")

    assert result["path"] == "README.md"
    assert result["content"] == "# FocusDen"


def test_github_repo_issues_tool_returns_assignees_and_labels() -> None:
    tool = GitHubRepoIssuesTool(client=FakeGitHubClient())  # type: ignore[arg-type]

    result = tool.execute(repository="FocusDen")

    issue = result["open_issues"][0]
    assert issue["assignees"] == ["levin"]
    assert issue["labels"] == ["enhancement"]


def test_github_repo_prs_tool_returns_author_and_status() -> None:
    tool = GitHubRepoPullRequestsTool(client=FakeGitHubClient())  # type: ignore[arg-type]

    result = tool.execute(repository="FocusDen")

    pull_request = result["open_pull_requests"][0]
    assert pull_request["author"] == "levin"
    assert pull_request["status"] == "open"


def test_github_create_issue_tool_returns_created_issue() -> None:
    tool = GitHubCreateIssueTool(client=FakeGitHubClient())  # type: ignore[arg-type]

    result = tool.execute(
        repository="FocusDen",
        title="Bug report",
        body="Something broke",
    )

    assert result["number"] == 7
    assert result["title"] == "Bug report"
    assert result["state"] == "open"


def test_github_repo_tool_returns_validation_error() -> None:
    tool = GitHubRepoInfoTool(client=FakeGitHubClient())  # type: ignore[arg-type]

    result = tool.execute(repository="")

    assert "error" in result
