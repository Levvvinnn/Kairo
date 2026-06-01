"""Placeholder GitHub API client."""


class GitHubClient:
    """Placeholder client for future GitHub API operations."""

    def __init__(self, token: str | None = None) -> None:
        """Initialize the GitHub client with an optional token."""
        self._token = token

    def is_configured(self) -> bool:
        """Return whether a GitHub token is available."""
        # TODO: Add token validation when GitHub integration is implemented.
        return bool(self._token)
