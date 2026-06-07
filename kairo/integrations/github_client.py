"""GitHub API client wrapper for Kairo tools."""

from __future__ import annotations

import base64
from typing import Any


class GitHubClient:
    """Small adapter around PyGithub used by Kairo tools."""

    def __init__(self, token: str | None = None) -> None:
        if token is None:
            from kairo.config.settings import settings

            token = settings.github_token

        self.github = self._create_client(token)

    def get_my_repos(self) -> list[str]:
        user = self.github.get_user()

        return [
            repo.full_name
            for repo in user.get_repos()
        ]

    def get_repo_info(self, repository: str) -> dict[str, Any]:
        repo = self._get_repository(repository)
        return {
            "name": repo.full_name,
            "description": repo.description,
            "language": repo.language,
            "stars": repo.stargazers_count,
            "forks": repo.forks_count,
            "open_issues": repo.open_issues_count,
            "default_branch": repo.default_branch,
        }

    def get_repo_readme(self, repository: str) -> dict[str, str]:
        repo = self._get_repository(repository)
        readme = repo.get_readme()
        content = self._decode_content(readme)
        return {
            "repository": repo.full_name,
            "path": readme.path,
            "content": content,
        }

    def get_repo_issues(self, repository: str) -> dict[str, Any]:
        repo = self._get_repository(repository)
        issues = []

        for issue in repo.get_issues(state="open"):
            if getattr(issue, "pull_request", None) is not None:
                continue

            issues.append({
                "number": issue.number,
                "title": issue.title,
                "state": issue.state,
                "author": issue.user.login if issue.user else None,
                "assignees": [assignee.login for assignee in issue.assignees],
                "labels": [label.name for label in issue.labels],
                "url": issue.html_url,
            })

        return {
            "repository": repo.full_name,
            "open_issues": issues,
        }

    def get_repo_pull_requests(self, repository: str) -> dict[str, Any]:
        repo = self._get_repository(repository)
        pull_requests = []

        for pull_request in repo.get_pulls(state="open"):
            pull_requests.append({
                "number": pull_request.number,
                "title": pull_request.title,
                "author": pull_request.user.login if pull_request.user else None,
                "status": pull_request.state,
                "url": pull_request.html_url,
            })

        return {
            "repository": repo.full_name,
            "open_pull_requests": pull_requests,
        }

    def create_issue(self, repository: str, title: str, body: str) -> dict[str, Any]:
        repo = self._get_repository(repository)
        issue = repo.create_issue(title=title, body=body)
        return {
            "repository": repo.full_name,
            "number": issue.number,
            "title": issue.title,
            "url": issue.html_url,
            "state": issue.state,
        }

    def _get_repository(self, repository: str) -> Any:
        normalized_repository = repository.strip()
        if not normalized_repository:
            raise ValueError("Repository is required")

        if "/" in normalized_repository:
            return self.github.get_repo(normalized_repository)

        user = self.github.get_user()
        login = user.login
        return self.github.get_repo(f"{login}/{normalized_repository}")

    @staticmethod
    def _decode_content(content_file: Any) -> str:
        decoded_content = getattr(content_file, "decoded_content", None)
        if isinstance(decoded_content, bytes):
            return decoded_content.decode("utf-8", errors="replace")
        if isinstance(decoded_content, str):
            return decoded_content

        encoded_content = getattr(content_file, "content", "")
        if isinstance(encoded_content, str):
            return base64.b64decode(encoded_content).decode("utf-8", errors="replace")

        raise ValueError("Unable to decode repository README")

    @staticmethod
    def _create_client(token: str | None) -> Any:
        try:
            from github import Github
        except ImportError as error:
            raise RuntimeError(
                "PyGithub is required for GitHub tools. Install requirements.txt."
            ) from error

        if not token:
            raise ValueError("GITHUB_TOKEN is required for GitHub tools")

        return Github(token)
