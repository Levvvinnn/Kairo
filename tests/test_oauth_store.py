import tempfile
import os
import json

from kairo.storage.oauth_store import TokenStore
from kairo.storage.database import Database


def test_token_store_roundtrip(tmp_path):
    db_path = tmp_path / "kairo_test.db"
    # Ensure Database creates schema
    db = Database(str(db_path))
    store = TokenStore()
    token = {"access_token": "abc", "refresh_token": "def", "expires_at": 9999999999}
    store.save_token("testprov", token)
    loaded = store.get_token("testprov")
    assert loaded is not None
    assert loaded.get("access_token") == "abc"
