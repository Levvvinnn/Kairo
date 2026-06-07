"""OAuth token persistence using the project's SQLite database.

Provides a TokenStore class that persists provider tokens (JSON blob)
into the `tokens` table on disk. It uses `sqlite3` directly to avoid
adding ORM dependencies.
"""

import json
import sqlite3
from typing import Any, Dict, Optional
from kairo.config.settings import settings
from kairo.storage.database import Database


class TokenStore:
    def __init__(self, db_path: Optional[str] = None):
        self.db = Database(db_path or settings.database_path)

    def _ensure(self) -> None:
        # Ensure DB initialized (Database.initialize will create tokens table)
        self.db.initialize()

    def save_token(self, provider: str, token: Dict[str, Any]) -> None:
        self._ensure()
        conn = sqlite3.connect(self.db.path)
        with conn:
            conn.execute(
                "INSERT OR REPLACE INTO tokens (provider, token_json) VALUES (?, ?)",
                (provider, json.dumps(token)),
            )

    def get_token(self, provider: str) -> Optional[Dict[str, Any]]:
        self._ensure()
        conn = sqlite3.connect(self.db.path)
        cur = conn.cursor()
        cur.execute("SELECT token_json FROM tokens WHERE provider = ?", (provider,))
        row = cur.fetchone()
        if not row:
            return None
        return json.loads(row[0])
