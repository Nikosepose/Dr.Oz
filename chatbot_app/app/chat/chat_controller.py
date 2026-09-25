"""Connect chat state to the chatbot logic without depending on the UI."""

from __future__ import annotations

from app.chat.chat_session import ChatSession
from app.logic.conversation_state import initialize_context
from app.logic.chatbot_engine import ChatbotEngine
from app.models.message import Message
from app.data.messages import GREETINGS


class ChatController:
    """Coordinate user messages, bot replies, and session startup."""

    def __init__(self, session: ChatSession, engine: ChatbotEngine) -> None:
        self.session = session
        self.engine = engine

    def start_session(self) -> Message:
        """Opprett riktig åpningsmelding én gang per samtale."""
        if self.session.initial_message is not None:
            return self.session.initial_message

        # Velg og lagre introduksjonsvariant før første tekst vises.
        initialize_context(self.session.context)
        greeting = GREETINGS[self.session.start_mode]

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
