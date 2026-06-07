"""SQLite persistence service for Kairo."""

from __future__ import annotations

import json

import sqlite3
from contextlib import closing
from pathlib import Path
from sqlite3 import Row
from typing import Any

from kairo.storage.models import MessageRecord, SessionRecord, ToolCallRecord


class Database:
    """Manages SQLite schema and persistence operations."""

    def __init__(self, database_path: str) -> None:
        """Initialize the database manager with a filesystem path."""
        self._database_path = Path(database_path)
        self.initialize()

    def initialize(self) -> None:
        """Create the SQLite schema if it does not already exist."""
        self._database_path.parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(self._database_path)) as connection:
            self._migrate_legacy_schema(connection)
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions(id)
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS tool_calls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    tool_name TEXT NOT NULL,
                    arguments TEXT NOT NULL,
                    result TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions(id)
                )
                """
            )
            # Tokens table for OAuth token storage
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS tokens (
                    provider TEXT PRIMARY KEY,
                    token_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.commit()

    @property
    def path(self) -> Path:
        """Return the configured SQLite database path."""
        return self._database_path

    def create_session(self) -> SessionRecord:
        """Create and return a new session."""
        with closing(self._connect()) as connection:
            cursor = connection.execute("INSERT INTO sessions DEFAULT VALUES")
            connection.commit()
            session_id = int(cursor.lastrowid)
            return self.get_session(session_id)

    def get_session(self, session_id: int) -> SessionRecord:
        """Return a session by ID."""
        with closing(self._connect()) as connection:
            row = connection.execute(
                "SELECT id, created_at FROM sessions WHERE id = ?",
                (session_id,),
            ).fetchone()

        if row is None:
            raise ValueError(f"Session not found: {session_id}")

        return self._session_from_row(row)

    def get_latest_session(self) -> SessionRecord | None:
        """Return the newest session, if one exists."""
        with closing(self._connect()) as connection:
            row = connection.execute(
                """
                SELECT id, created_at
                FROM sessions
                ORDER BY id DESC
                LIMIT 1
                """
            ).fetchone()

        if row is None:
            return None
        return self._session_from_row(row)

    def get_or_create_latest_session(self) -> SessionRecord:
        """Return the latest session or create one if the database is empty."""
        latest_session = self.get_latest_session()
        if latest_session is not None:
            return latest_session
        return self.create_session()

    def add_message(self, session_id: int, role: str, content: str) -> MessageRecord:
        """Persist and return a conversation message."""
        if role not in {"user", "assistant"}:
            raise ValueError(f"Unsupported message role: {role}")

        with closing(self._connect()) as connection:
            cursor = connection.execute(
                """
                INSERT INTO messages (session_id, role, content)
                VALUES (?, ?, ?)
                """,
                (session_id, role, content),
            )
            connection.commit()
            message_id = int(cursor.lastrowid)
            row = connection.execute(
                """
                SELECT id, session_id, role, content, created_at
                FROM messages
                WHERE id = ?
                """,
                (message_id,),
            ).fetchone()

        if row is None:
            raise RuntimeError("Failed to load persisted message")
        return self._message_from_row(row)

    def list_messages(self, session_id: int) -> list[MessageRecord]:
        """Return messages for a session in chronological order."""
        with closing(self._connect()) as connection:
            rows = connection.execute(
                """
                SELECT id, session_id, role, content, created_at
                FROM messages
                WHERE session_id = ?
                ORDER BY id ASC
                """,
                (session_id,),
            ).fetchall()

        return [self._message_from_row(row) for row in rows]

    def add_tool_call(
        self,
        session_id: int,
        tool_name: str,
        arguments: dict[str, Any],
        result: Any,
    ) -> ToolCallRecord:
        """Persist and return a tool execution record."""
        serialized_arguments = self._to_json(arguments)
        serialized_result = self._to_json(result)

        with closing(self._connect()) as connection:
            cursor = connection.execute(
                """
                INSERT INTO tool_calls (session_id, tool_name, arguments, result)
                VALUES (?, ?, ?, ?)
                """,
                (session_id, tool_name, serialized_arguments, serialized_result),
            )
            connection.commit()
            tool_call_id = int(cursor.lastrowid)
            row = connection.execute(
                """
                SELECT id, session_id, tool_name, arguments, result, created_at
                FROM tool_calls
                WHERE id = ?
                """,
                (tool_call_id,),
            ).fetchone()

        if row is None:
            raise RuntimeError("Failed to load persisted tool call")
        return self._tool_call_from_row(row)

    def list_tool_calls(self, session_id: int) -> list[ToolCallRecord]:
        """Return tool executions for a session in chronological order."""
        with closing(self._connect()) as connection:
            rows = connection.execute(
                """
                SELECT id, session_id, tool_name, arguments, result, created_at
                FROM tool_calls
                WHERE session_id = ?
                ORDER BY id ASC
                """,
                (session_id,),
            ).fetchall()

        return [self._tool_call_from_row(row) for row in rows]

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._database_path)
        connection.row_factory = Row
        return connection

    @staticmethod
    def _to_json(value: Any) -> str:
        try:
            return json.dumps(value, ensure_ascii=True, default=str)
        except TypeError:
            return json.dumps(str(value), ensure_ascii=True)

    @staticmethod
    def _session_from_row(row: Row) -> SessionRecord:
        return SessionRecord(id=row["id"], created_at=row["created_at"])

    @staticmethod
    def _message_from_row(row: Row) -> MessageRecord:
        return MessageRecord(
            id=row["id"],
            session_id=row["session_id"],
            role=row["role"],
            content=row["content"],
            created_at=row["created_at"],
        )

    @staticmethod
    def _tool_call_from_row(row: Row) -> ToolCallRecord:
        return ToolCallRecord(
            id=row["id"],
            session_id=row["session_id"],
            tool_name=row["tool_name"],
            arguments=row["arguments"],
            result=row["result"],
            created_at=row["created_at"],
        )

    @staticmethod
    def _migrate_legacy_schema(connection: sqlite3.Connection) -> None:
        table_names = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }

        if "conversations" in table_names and "sessions" not in table_names:
            connection.execute("ALTER TABLE conversations RENAME TO sessions")

        message_columns = {
            row[1]
            for row in connection.execute("PRAGMA table_info(messages)").fetchall()
        }
        if "messages" in table_names and "conversation_id" in message_columns:
            connection.execute("ALTER TABLE messages RENAME TO legacy_messages")
            connection.execute(
                """
                CREATE TABLE messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions(id)
                )
                """
            )
            connection.execute(
                """
                INSERT INTO messages (id, session_id, role, content, created_at)
                SELECT id, conversation_id, role, content, created_at
                FROM legacy_messages
                """
            )
            connection.execute("DROP TABLE legacy_messages")
