"""Conversation session management."""

from __future__ import annotations

from typing import TypedDict

from kairo.storage.database import Database


class ChatMessage(TypedDict):
    """Message shape expected by the LLM provider."""

    role: str
    content: str


class ConversationManager:
    """Keeps in-memory history synchronized with SQLite persistence."""

    def __init__(self, database: Database | None = None) -> None:
        if database is None:
            from kairo.config.settings import settings

            database = Database(settings.database_path)

        self.database = database
        self.session = self.database.get_or_create_latest_session()
        self.messages: list[ChatMessage] = []
        self.load_history()

    @property
    def session_id(self) -> int:
        """Return the active session ID."""
        return self.session.id

    def new_session(self) -> int:
        """Create a new active session and clear in-memory history."""
        self.session = self.database.create_session()
        self.messages = []
        return self.session.id

    def load_history(self) -> None:
        """Load persisted history for the active session."""
        self.messages = [
            {"role": message.role, "content": message.content}
            for message in self.database.list_messages(self.session.id)
        ]

    def add_user(self, content: str) -> None:
        """Add and persist a user message."""
        self.database.add_message(self.session.id, "user", content)
        self.messages.append({
            "role": "user",
            "content": content
        })

    def add_assistant(self, content: str) -> None:
        """Add and persist an assistant message."""
        self.database.add_message(self.session.id, "assistant", content)
        self.messages.append({
            "role": "assistant",
            "content": content
        })

    def add_context(self, content: str) -> None:
        """Add non-persisted context for the current agent loop."""
        self.messages.append({
            "role": "user",
            "content": content
        })

    def get_messages(self) -> list[ChatMessage]:
        """Return a copy of the active conversation history."""
        return list(self.messages)
