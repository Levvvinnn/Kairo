"""Typed persistence models for Kairo storage records."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class SessionRecord(BaseModel):
    """A persisted Kairo chat session."""

    id: int
    created_at: str

    model_config = ConfigDict(frozen=True)


class MessageRecord(BaseModel):
    """A persisted conversation message."""

    id: int
    session_id: int
    role: str
    content: str
    created_at: str

    model_config = ConfigDict(frozen=True)


class ToolCallRecord(BaseModel):
    """A persisted tool execution."""

    id: int
    session_id: int
    tool_name: str
    arguments: str
    result: str
    created_at: str

    model_config = ConfigDict(frozen=True)
