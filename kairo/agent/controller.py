from __future__ import annotations

import json
from typing import Any

from rich.console import Console

from kairo.agent.conversation import ChatMessage, ConversationManager
from kairo.agent.prompts import PROJECT_ANALYSIS_PROMPT, SYSTEM_PROMPT
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
        if "analyze" in lowered_input and "project" in lowered_input:
            return PROJECT_ANALYSIS_PROMPT
        if "architecture" in lowered_input and "project" in lowered_input:
            return PROJECT_ANALYSIS_PROMPT
        return SYSTEM_PROMPT
