"""SQLite database initialization for Kairo."""

import sqlite3
from pathlib import Path


class Database:
    """Manages SQLite database initialization and connections."""

    def __init__(self, database_path: str) -> None:
        """Initialize the database manager with a filesystem path."""
        self._database_path = Path(database_path)

    def initialize(self) -> None:
        """Create the initial SQLite schema if it does not already exist."""
        self._database_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self._database_path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
                )
                """
            )
            connection.commit()
        # TODO: Add migrations before evolving the schema beyond this bootstrap.

    @property
    def path(self) -> Path:
        """Return the configured SQLite database path."""
        return self._database_path
