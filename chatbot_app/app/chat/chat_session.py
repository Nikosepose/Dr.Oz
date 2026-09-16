"""State belonging to an individual chat session."""

from __future__ import annotations

from uuid import uuid4

from app.chat.chat_context import ChatContext
from app.models.message import Message


class ChatSession:
    """Keep a session's messages and context independent of other sessions."""

    def __init__(self, start_mode: str = "direct") -> None:
        if start_mode not in {"direct", "introduction"}:
            raise ValueError("start_mode must be 'direct' or 'introduction'.")

        self.session_id = str(uuid4())
        self.start_mode = start_mode
        self.context = ChatContext()
        self.messages: list[Message] = []
        self.initial_message: Message | None = None

    def add_message(self, message: Message) -> None:
        self.messages.append(message)

    def get_messages(self) -> list[Message]:
        """Return a copy so callers cannot accidentally modify the message list."""
        return list(self.messages)
