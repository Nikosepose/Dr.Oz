"""Connect chat state to the chatbot logic without depending on the UI."""

from __future__ import annotations

from app.chat.chat_session import ChatSession
from app.logic.chatbot_engine import ChatbotEngine
from app.models.message import Message


class ChatController:
    """Coordinate user messages, bot replies, and session startup."""

    def __init__(self, session: ChatSession, engine: ChatbotEngine) -> None:
        self.session = session
        self.engine = engine

    def start_session(self) -> Message:
        """Create the selected greeting once, even if startup is called again."""
        if self.session.initial_message is not None:
            return self.session.initial_message

        if self.session.start_mode == "introduction":
            greeting = (
                "Hello! This is currently a dummy chatbot.\n\n"
                "For now, I can echo your messages and keep the conversation "
                "history while this chat is open. Future versions may collect "
                "information and use it to guide the conversation.\n\n"
                "What would you like to talk about?"
            )
        else:
            greeting = "Hello! How can I help you today?"

        message = Message(sender="bot", text=greeting)
        self.session.add_message(message)
        self.session.initial_message = message
        return message

    def handle_user_message(self, text: str) -> Message | None:
        """Record nonempty input and pass it to the engine with session context."""
        text = text.strip()
        if not text:
            return None

        self.session.add_message(Message(sender="user", text=text))
        reply = self.engine.process_message(text, self.session.context)
        message = Message(sender="bot", text=reply)
        self.session.add_message(message)
        return message
