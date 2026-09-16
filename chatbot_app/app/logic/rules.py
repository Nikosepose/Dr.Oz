"""Placeholder for rules that can inspect or update conversation context."""

from __future__ import annotations

from app.chat.chat_context import ChatContext


def apply_rules(text: str, context: ChatContext) -> str | None:
    """Return a reply for a matching rule, or None to use the engine's fallback."""
    # Add custom rules here, using context.get/set to retain session information.
    return None
