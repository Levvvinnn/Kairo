"""Google Workspace REST clients (Gmail, Calendar, Docs, Drive).

These are lightweight wrappers that use an OAuth access token retrieved
from the persistent token store. They expect an access token with
appropriate scopes configured for the Google APIs being used.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import requests

from kairo.config.settings import settings
from kairo.storage.oauth_store import TokenStore


class BaseGoogleClient:
    def __init__(self, token_store: Optional[TokenStore] = None, token_name: str = "google"):
        self.token_store = token_store or TokenStore()
        self.token_name = token_name

    def _get_headers(self) -> Dict[str, str]:
        token = self.token_store.get_token(self.token_name)
        if not token or "access_token" not in token:
            raise RuntimeError("No OAuth access token available for Google APIs")
        return {"Authorization": f"Bearer {token['access_token']}"}


class GmailClient(BaseGoogleClient):
    base = "https://gmail.googleapis.com/gmail/v1"

    def list_unread(self, max_results: int = 20) -> List[Dict[str, Any]]:
        headers = self._get_headers()
        resp = requests.get(f"{self.base}/users/me/messages", headers=headers, params={"q": "is:unread", "maxResults": max_results}, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return data.get("messages", [])

    def get_message(self, message_id: str) -> Dict[str, Any]:
        headers = self._get_headers()
        resp = requests.get(f"{self.base}/users/me/messages/{message_id}", headers=headers, params={"format": "full"}, timeout=15)
        resp.raise_for_status()
        return resp.json()

    def search(self, query: str, max_results: int = 50) -> List[Dict[str, Any]]:
        headers = self._get_headers()
        resp = requests.get(f"{self.base}/users/me/messages", headers=headers, params={"q": query, "maxResults": max_results}, timeout=15)
        resp.raise_for_status()
        return resp.json().get("messages", [])


class CalendarClient(BaseGoogleClient):
    base = "https://www.googleapis.com/calendar/v3"

    def list_events(self, calendar_id: str = "primary", max_results: int = 50) -> List[Dict[str, Any]]:
        headers = self._get_headers()
        resp = requests.get(f"{self.base}/calendars/{calendar_id}/events", headers=headers, params={"maxResults": max_results}, timeout=15)
        resp.raise_for_status()
        return resp.json().get("items", [])

    def create_event(self, event: Dict[str, Any], calendar_id: str = "primary") -> Dict[str, Any]:
        headers = self._get_headers()
        resp = requests.post(f"{self.base}/calendars/{calendar_id}/events", headers={**headers, "Content-Type": "application/json"}, json=event, timeout=15)
        resp.raise_for_status()
        return resp.json()


class DocsClient(BaseGoogleClient):
    base = "https://docs.googleapis.com/v1"

    def create_document(self, title: str) -> Dict[str, Any]:
        headers = self._get_headers()
        resp = requests.post(f"{self.base}/documents", headers={**headers, "Content-Type": "application/json"}, json={"title": title}, timeout=15)
        resp.raise_for_status()
        return resp.json()

    def get_document(self, document_id: str) -> Dict[str, Any]:
        headers = self._get_headers()
        resp = requests.get(f"{self.base}/documents/{document_id}", headers=headers, timeout=15)
        resp.raise_for_status()
        return resp.json()


class DriveClient(BaseGoogleClient):
    base = "https://www.googleapis.com/drive/v3"

    def search_files(self, query: str, page_size: int = 50) -> List[Dict[str, Any]]:
        headers = self._get_headers()
        resp = requests.get(f"{self.base}/files", headers=headers, params={"q": query, "pageSize": page_size, "fields": "files(id,name,mimeType,owners)"}, timeout=15)
        resp.raise_for_status()
        return resp.json().get("files", [])

    def get_file(self, file_id: str) -> Dict[str, Any]:
        headers = self._get_headers()
        resp = requests.get(f"{self.base}/files/{file_id}", headers=headers, params={"fields": "id,name,mimeType,owners"}, timeout=15)
        resp.raise_for_status()
        return resp.json()
