"""Conversation primitives for Kairo agent sessions."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Message:
    """Represents a single message in a conversation."""

    role: str
    content: str


@dataclass
class Conversation:
    """Stores ordered messages for an agent conversation."""

    messages: list[Message] = field(default_factory=list)

    def add_message(self, role: str, content: str) -> None:
        """Append a message to the conversation."""
        # TODO: Validate roles against the supported model provider schema.
        self.messages.append(Message(role=role, content=content))
