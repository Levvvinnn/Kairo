from __future__ import annotations

import json
from typing import Any

from rich.console import Console

from kairo.agent.conversation import ChatMessage, ConversationManager
from kairo.agent.prompts import (
    PROJECT_ANALYSIS_PROMPT,
    REPOSITORY_ANALYSIS_PROMPT,
    SYSTEM_PROMPT,
)
from kairo.llm.gemini import GeminiProvider
from kairo.tools.registry import create_default_registry


class AgentController:
    """Coordinates the provider, conversation history, and tool execution."""

    max_iterations = 5

    def __init__(self) -> None:
        self.provider = GeminiProvider()
        self.conversation = ConversationManager()
        self.console = Console()

        self.registry = create_default_registry()

    @property
    def session_id(self) -> int:
        """Return the active conversation session ID."""
        return self.conversation.session_id

    def new_session(self) -> int:
        """Start a new conversation session."""
        return self.conversation.new_session()

    def chat(self, user_input: str) -> str:
        """Run a multi-step agent loop for one user message."""
        self.conversation.add_user(user_input)
        system_prompt = self._system_prompt_for(user_input)

        for _ in range(self.max_iterations):
            response = self.provider.chat(self._build_messages(system_prompt))
            tool_calls = self._parse_tool_calls(response)

            if not tool_calls:
                self.conversation.add_assistant(response)
                return response

            self.conversation.add_assistant(response)
            for tool_call in tool_calls:
                result = self._execute_tool_call(tool_call)
                self.conversation.add_context(
                    self._format_tool_result(tool_call, result)
                )

        final_response = self.provider.chat(
            self._build_messages(
                system_prompt,
                extra_context=(
                    "You have reached the maximum tool iteration limit. "
                    "Use the available conversation and tool results to answer now."
                ),
            )
        )
        self.conversation.add_assistant(final_response)
        return final_response

    def _build_messages(
        self,
        system_prompt: str,
        extra_context: str | None = None,
    ) -> list[ChatMessage]:
        messages: list[ChatMessage] = [
            {
                "role": "system",
                "content": system_prompt,
            }
        ]
        if extra_context is not None:
            messages.append({"role": "system", "content": extra_context})
        messages.extend(self.conversation.get_messages())
        return messages

    def _execute_tool_call(self, tool_call: dict[str, Any]) -> Any:
        tool_name = str(tool_call["tool"])
        arguments = tool_call.get("arguments", {})

        self.console.print(f"[bold cyan][Kairo][/bold cyan] Executing tool: {tool_name}")

        if not isinstance(arguments, dict):
            result = {
                "error": f"Tool arguments must be an object: {tool_name}",
                "tool": tool_name,
            }
            persisted_arguments: dict[str, Any] = {}
        else:
            persisted_arguments = arguments

        try:
            if not isinstance(arguments, dict):
                raise ValueError(result["error"])
            result = self.registry.execute(tool_name, **arguments)
        except Exception as error:
            result = {
                "error": str(error),
                "tool": tool_name,
            }

        self.conversation.database.add_tool_call(
            session_id=self.conversation.session_id,
            tool_name=tool_name,
            arguments=persisted_arguments,
            result=result,
        )
        return result

    def _parse_tool_calls(self, response: str) -> list[dict[str, Any]]:
        try:
            parsed = json.loads(self._clean_json(response))
        except json.JSONDecodeError:
            return []

        if isinstance(parsed, dict) and "tool" in parsed:
            return [parsed]

        if isinstance(parsed, list):
            return [
                item
                for item in parsed
                if isinstance(item, dict) and "tool" in item
            ]

        return []

    @staticmethod
    def _clean_json(response: str) -> str:
        stripped = response.strip()
        if stripped.startswith("```json"):
            return stripped.removeprefix("```json").removesuffix("```").strip()
        if stripped.startswith("```"):
            return stripped.removeprefix("```").removesuffix("```").strip()
        return stripped

    @staticmethod
    def _format_tool_result(tool_call: dict[str, Any], result: Any) -> str:
        payload = {
            "tool": tool_call.get("tool"),
            "arguments": tool_call.get("arguments", {}),
            "result": result,
        }
        return f"Tool result:\n{json.dumps(payload, ensure_ascii=True, default=str)}"

    @staticmethod
    def _system_prompt_for(user_input: str) -> str:
        lowered_input = user_input.lower()
        if "repository" in lowered_input or "repo" in lowered_input:
            if "analyze" in lowered_input or "review" in lowered_input:
                return REPOSITORY_ANALYSIS_PROMPT
        if "analyze" in lowered_input and "project" in lowered_input:
            return PROJECT_ANALYSIS_PROMPT
        if "architecture" in lowered_input and "project" in lowered_input:
            return PROJECT_ANALYSIS_PROMPT
        return SYSTEM_PROMPT

    def weekly_planner(self) -> str:
        """Produce a weekly planner by aggregating assignments, events, and unread emails."""
        from datetime import datetime, timedelta, timezone

        now = datetime.now(timezone.utc)
        week_later = now + timedelta(days=7)

        summary_parts = []

        # Canvas assignments due in next 7 days
        try:
            courses = self.registry.execute("canvas_courses")
            upcoming_assignments = []
            for course in courses:
                course_id = course.get("id")
                assignments = self.registry.execute("canvas_assignments", course_id=course_id)
                for a in assignments:
                    due = a.get("due_at")
                    if due:
                        try:
                            due_dt = datetime.fromisoformat(due.replace("Z", "+00:00"))
                        except Exception:
                            continue
                        if now <= due_dt <= week_later:
                            upcoming_assignments.append({"course": course.get("name"), "assignment": a.get("name"), "due": due})
            summary_parts.append(f"Upcoming assignments: {len(upcoming_assignments)}")
            for a in upcoming_assignments[:10]:
                summary_parts.append(f"- {a['course']}: {a['assignment']} due {a['due']}")
        except Exception as e:
            summary_parts.append(f"Canvas assignments: error: {e}")

        # Calendar events next week
        try:
            events = self.registry.execute("calendar_events")
            upcoming_events = []
            for ev in events:
                start = ev.get("start", {}).get("dateTime") or ev.get("start", {}).get("date")
                if start:
                    upcoming_events.append({"summary": ev.get("summary"), "when": start})
            summary_parts.append(f"Upcoming events: {len(upcoming_events)}")
            for ev in upcoming_events[:10]:
                summary_parts.append(f"- {ev['when']}: {ev['summary']}")
        except Exception as e:
            summary_parts.append(f"Calendar events: error: {e}")

        # Unread emails
        try:
            unread = self.registry.execute("gmail_unread")
            summary_parts.append(f"Unread emails: {len(unread)}")
        except Exception as e:
            summary_parts.append(f"Gmail unread: error: {e}")

        # Generate study plan placeholder
        summary_parts.append("Suggested study schedule: \n- Block 2hrs daily for readings; prioritize assignments by due date.")

        return "\n".join(summary_parts)

    def daily_briefing(self) -> str:
        """Produce a daily briefing for the next 24 hours."""
        from datetime import datetime, timedelta, timezone

        now = datetime.now(timezone.utc)
        tomorrow = now + timedelta(days=1)

        parts = []
        try:
            events = self.registry.execute("calendar_events")
            todays = [e for e in events if True][:10]
            parts.append(f"Events today: {len(todays)}")
        except Exception as e:
            parts.append(f"Calendar: error: {e}")

        try:
            unread = self.registry.execute("gmail_unread")
            parts.append(f"Unread emails: {len(unread)}")
        except Exception as e:
            parts.append(f"Gmail: error: {e}")

        try:
            courses = self.registry.execute("canvas_courses")
            due_today = []
            for course in courses:
                assignments = self.registry.execute("canvas_assignments", course_id=course.get("id"))
                for a in assignments:
                    due = a.get("due_at")
                    if due:
                        try:
                            due_dt = datetime.fromisoformat(due.replace("Z", "+00:00"))
                        except Exception:
                            continue
                        if now <= due_dt <= tomorrow:
                            due_today.append({"course": course.get("name"), "assignment": a.get("name"), "due": due})
            parts.append(f"Assignments due soon: {len(due_today)}")
        except Exception as e:
            parts.append(f"Canvas: error: {e}")

        parts.append("Priorities: Finish assignments due soon; attend meetings; respond to urgent emails.")
        return "\n".join(parts)
