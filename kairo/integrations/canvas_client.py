"""Simple Canvas LMS client wrapper using the Canvas REST API.

This client supports token-based access via an API token configured in
the environment (CANVAS_API_TOKEN). It provides methods used by the
tooling layer: list courses, list assignments for a course, list
announcements, and fetch grades/submissions.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import requests

from kairo.config.settings import settings


class CanvasClient:
    def __init__(self, base_url: Optional[str] = None, token: Optional[str] = None):
        self.base_url = (base_url or settings.canvas_base_url or "").rstrip("/")
        self.token = token or settings.canvas_api_token
        if not self.base_url or not self.token:
            # Client can be constructed without credentials for static analysis,
            # but most methods will raise if used without a token.
            self._headers = {}
        else:
            self._headers = {"Authorization": f"Bearer {self.token}"}

    def _url(self, path: str) -> str:
        # Canvas API v1
        return f"{self.base_url}/api/v1{path}"

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        if not self._headers:
            raise RuntimeError("Canvas client not configured with API token or base URL")
        resp = requests.get(self._url(path), headers=self._headers, params=params, timeout=15)
        resp.raise_for_status()
        return resp.json()

    def get_courses(self) -> List[Dict[str, Any]]:
        """Return list of visible courses for the authenticated user."""
        return self._get("/courses", params={"per_page": 100})

    def get_assignments(self, course_id: int) -> List[Dict[str, Any]]:
        """Return assignments for a given course."""
        return self._get(f"/courses/{course_id}/assignments", params={"per_page": 100})

    def get_announcements(self, course_id: int) -> List[Dict[str, Any]]:
        """Return announcements (discussion topics flagged as announcements)."""
        return self._get(f"/courses/{course_id}/discussion_topics", params={"only_announcements": 1, "per_page": 100})

    def get_grades(self, course_id: int, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Return submissions/grade summaries for a course. If user_id is provided,
        filter to that user (may require different API call depending on Canvas setup).
        """
        params = {"per_page": 100}
        if user_id is not None:
            params["student_ids[]"] = user_id
        return self._get(f"/courses/{course_id}/students/submissions", params=params)
