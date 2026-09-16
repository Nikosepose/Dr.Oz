"""Dummy response engine that can be replaced with application-specific logic."""

from __future__ import annotations

from app.chat.chat_context import ChatContext
from app.logic import rules


class ChatbotEngine:
    """Use a matching rule or return a placeholder response."""

    def process_message(self, text: str, context: ChatContext) -> str:
        """Add real chatbot behavior here while keeping the controller unchanged."""
        response = rules.apply_rules(text, context)
        if response is not None:
            return response
        return f"Dummy chatbot received: {text}"
