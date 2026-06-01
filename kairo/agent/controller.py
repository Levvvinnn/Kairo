"""Agent controller for coordinating conversations and tools."""

from kairo.agent.conversation import Conversation
from kairo.config.settings import Settings
from kairo.tools.registry import ToolRegistry


class AgentController:
    """Coordinates agent state, model access, and tool execution."""

    def __init__(self, settings: Settings, tool_registry: ToolRegistry) -> None:
        """Initialize the controller with settings and available tools."""
        self._settings = settings
        self._tool_registry = tool_registry
        self._conversation = Conversation()

    def start_chat(self) -> str:
        """Start a placeholder chat flow."""
        # TODO: Replace with an OpenAI-compatible agent loop.
        return "Welcome to Kairo"

    @property
    def conversation(self) -> Conversation:
        """Return the active conversation."""
        return self._conversation

    @property
    def tool_registry(self) -> ToolRegistry:
        """Return the tool registry available to the agent."""
        return self._tool_registry
