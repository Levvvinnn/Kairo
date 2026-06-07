"""Canvas LMS tools for Kairo.

Provides a set of tools that expose Canvas data to the agent: courses,
assignments, announcements, and grades.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from kairo.tools.base import Tool
from kairo.integrations.canvas_client import CanvasClient


class CanvasCoursesTool(Tool):
    name = "canvas_courses"
    description = "List Canvas courses for the authenticated user."

    def __init__(self, client: Optional[CanvasClient] = None):
        self.client = client or CanvasClient()

    def execute(self, **kwargs) -> Any:
        return self.client.get_courses()


class CanvasAssignmentsTool(Tool):
    name = "canvas_assignments"
    description = "List assignments for a given Canvas course. Arguments: course_id (int)."

    def __init__(self, client: Optional[CanvasClient] = None):
        self.client = client or CanvasClient()

    def execute(self, **kwargs) -> Any:
        course_id = kwargs.get("course_id")
        if course_id is None:
            raise ValueError("course_id is required")
        return self.client.get_assignments(int(course_id))


class CanvasAnnouncementsTool(Tool):
    name = "canvas_announcements"
    description = "List announcements for a Canvas course. Arguments: course_id (int)."

    def __init__(self, client: Optional[CanvasClient] = None):
        self.client = client or CanvasClient()

    def execute(self, **kwargs) -> Any:
        course_id = kwargs.get("course_id")
        if course_id is None:
            raise ValueError("course_id is required")
        return self.client.get_announcements(int(course_id))


class CanvasGradesTool(Tool):
    name = "canvas_grades"
    description = "Fetch grades/submissions for a course. Arguments: course_id (int), user_id (optional int)."

    def __init__(self, client: Optional[CanvasClient] = None):
        self.client = client or CanvasClient()

    def execute(self, **kwargs) -> Any:
        course_id = kwargs.get("course_id")
        user_id = kwargs.get("user_id")
        if course_id is None:
            raise ValueError("course_id is required")
        return self.client.get_grades(int(course_id), int(user_id) if user_id is not None else None)
