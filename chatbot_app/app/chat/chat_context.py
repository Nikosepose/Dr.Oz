"""Conversation data shared with the chatbot's logic."""

from __future__ import annotations

from typing import Any


class ChatContext:
    """Store arbitrary values for one conversation."""

    def __init__(self) -> None:
        self.data: dict[str, Any] = {}

    def set(self, key: str, value: Any) -> None:
        self.data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def has(self, key: str) -> bool:
        return key in self.data

    def remove(self, key: str) -> None:
        self.data.pop(key, None)

    def clear(self) -> None:
        self.data.clear()
