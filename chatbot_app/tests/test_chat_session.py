import unittest
from datetime import timedelta
from uuid import UUID

from app.chat.chat_session import ChatSession
from app.models.message import Message


class ChatSessionTests(unittest.TestCase):
    def test_sessions_have_distinct_ids_contexts_and_histories(self):
        first = ChatSession()
        second = ChatSession(start_mode="introduction")
        self.assertEqual(str(UUID(first.session_id)), first.session_id)
        self.assertNotEqual(first.session_id, second.session_id)
        self.assertEqual(first.start_mode, "direct")
        self.assertEqual(second.start_mode, "introduction")

        first.context.set("name", "Ada")
        message = Message(sender="user", text="Hello")
        first.add_message(message)
        self.assertFalse(second.context.has("name"))
        self.assertEqual(second.get_messages(), [])
        self.assertEqual(first.get_messages(), [message])

        history = first.get_messages()
        history.clear()
        self.assertEqual(first.get_messages(), [message])

    def test_invalid_start_mode_is_rejected(self):
        with self.assertRaises(ValueError):
            ChatSession(start_mode="unknown")

    def test_messages_have_utc_timestamps_and_valid_senders(self):
        for sender in ("user", "bot"):
            message = Message(sender=sender, text="Hello")
            self.assertEqual(message.timestamp.utcoffset(), timedelta(0))
        with self.assertRaises(ValueError):
            Message(sender="unknown", text="Hello")
