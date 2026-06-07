"""Tools exposing Google Workspace features to the agent."""

from __future__ import annotations

from typing import Any, Dict, Optional

from kairo.tools.base import Tool
from kairo.integrations.google_workspace import (
    GmailClient,
    CalendarClient,
    DocsClient,
    DriveClient,
)


class GmailUnreadTool(Tool):
    name = "gmail_unread"
    description = "Return summaries of unread Gmail messages."

    def __init__(self, client: Optional[GmailClient] = None):
        self.client = client or GmailClient()

    def execute(self, **kwargs) -> Any:
        return self.client.list_unread()


class GmailSearchTool(Tool):
    name = "gmail_search"
    description = "Search Gmail with a query string. Arguments: query (str)."

    def __init__(self, client: Optional[GmailClient] = None):
        self.client = client or GmailClient()

    def execute(self, **kwargs) -> Any:
        query = kwargs.get("query")
        if not query:
            raise ValueError("query is required")
        return self.client.search(query)


class CalendarEventsTool(Tool):
    name = "calendar_events"
    description = "List calendar events. Arguments: calendar_id (optional)."

    def __init__(self, client: Optional[CalendarClient] = None):
        self.client = client or CalendarClient()

    def execute(self, **kwargs) -> Any:
        calendar_id = kwargs.get("calendar_id", "primary")
        return self.client.list_events(calendar_id=calendar_id)


class CalendarCreateEventTool(Tool):
    name = "calendar_create_event"
    description = "Create a calendar event. Arguments: event (dict), calendar_id (optional)."

    def __init__(self, client: Optional[CalendarClient] = None):
        self.client = client or CalendarClient()

    def execute(self, **kwargs) -> Any:
        event = kwargs.get("event")
        calendar_id = kwargs.get("calendar_id", "primary")
        if event is None:
            raise ValueError("event is required")
        return self.client.create_event(event=event, calendar_id=calendar_id)


class DocsCreateTool(Tool):
    name = "docs_create"
    description = "Create a Google Doc. Arguments: title (str)."

    def __init__(self, client: Optional[DocsClient] = None):
        self.client = client or DocsClient()

    def execute(self, **kwargs) -> Any:
        title = kwargs.get("title")
        if not title:
            raise ValueError("title is required")
        return self.client.create_document(title=title)


class DocsReadTool(Tool):
    name = "docs_read"
    description = "Read a Google Doc. Arguments: document_id (str)."

    def __init__(self, client: Optional[DocsClient] = None):
        self.client = client or DocsClient()

    def execute(self, **kwargs) -> Any:
        document_id = kwargs.get("document_id")
        if not document_id:
            raise ValueError("document_id is required")
        return self.client.get_document(document_id=document_id)


class DriveSearchTool(Tool):
    name = "drive_search"
    description = "Search Drive files. Arguments: query (str)."

    def __init__(self, client: Optional[DriveClient] = None):
        self.client = client or DriveClient()

    def execute(self, **kwargs) -> Any:
        query = kwargs.get("query")
        if not query:
            raise ValueError("query is required")
        return self.client.search_files(query=query)


class DriveReadFileTool(Tool):
    name = "drive_read"
    description = "Get Drive file metadata. Arguments: file_id (str)."

    def __init__(self, client: Optional[DriveClient] = None):
        self.client = client or DriveClient()

    def execute(self, **kwargs) -> Any:
        file_id = kwargs.get("file_id")
        if not file_id:
            raise ValueError("file_id is required")
        return self.client.get_file(file_id=file_id)
