"""Base abstractions for Kairo tools."""

from abc import ABC, abstractmethod
from typing import Any


class Tool(ABC):
    """Abstract base class for executable Kairo tools."""

    name: str
    description: str

    @abstractmethod
    def execute(self, **kwargs: Any) -> str:
        """Execute the tool and return a human-readable result."""
