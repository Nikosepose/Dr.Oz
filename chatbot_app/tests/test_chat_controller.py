import unittest

from app.chat.chat_controller import ChatController
from app.chat.chat_session import ChatSession
from app.data.messages import GREETINGS, INITIAL_PROMPT, NAME_PROMPT, get_name_reply
from app.logic.chatbot_engine import ChatbotEngine

class RecordingEngine:
    """An example replacement engine that uses the session's shared context."""

    def __init__(self):
        self.calls = []

    def process_message(self, text, context):
        self.calls.append((text, context))
        count = context.get("turn_count", 0) + 1
        context.set("turn_count", count)
        return f"Reply {count}: {text}"


class ChatControllerTests(unittest.TestCase):
    def test_both_start_modes_ask_name_then_process_symptoms(self):
        for mode in ("direct", "introduction"):
            with self.subTest(mode=mode):
                session = ChatSession(start_mode=mode)
                controller = ChatController(session, ChatbotEngine())
                greeting = controller.start_session()
                self.assertIn(NAME_PROMPT, greeting.text)
                self.assertNotIn(INITIAL_PROMPT, greeting.text)

                reply = controller.handle_user_message("  Nora  ")
                self.assertEqual(
                    reply.text,
                    get_name_reply("Nora", session.context.get("introduction_id")),
                )
                self.assertIn("Nora", reply.text)
                self.assertIn(INITIAL_PROMPT, reply.text)
                self.assertEqual(session.context.get("user_name"), "Nora")
                self.assertEqual(session.context.get("stage"), "initial")
                self.assertIsNone(session.context.get("pending_question"))

                reply = controller.handle_user_message("Jeg har feber")
                self.assertEqual(session.context.get("stage"), "questions")
                self.assertEqual(session.context.get("patient_state")["fever"], "present")
                self.assertEqual(session.context.get("answered_questions"), 0)
                self.assertIn(session.context.get("pending_question"), reply.text)
                self.assertEqual(len(session.get_messages()), 5)

    def test_names_are_independent_between_sessions(self):
        engine = ChatbotEngine()
        first_session = ChatSession()
        second_session = ChatSession(start_mode="introduction")
        first = ChatController(first_session, engine)
        second = ChatController(second_session, engine)
        first.start_session()
        second.start_session()

        first.handle_user_message("Nora")
        self.assertIsNone(second_session.context.get("user_name"))
        reply = second.handle_user_message("Ada")

        self.assertEqual(first_session.context.get("user_name"), "Nora")
        self.assertEqual(second_session.context.get("user_name"), "Ada")
        self.assertEqual(
            reply.text,
            get_name_reply("Ada", second_session.context.get("introduction_id")),
        )
        self.assertEqual(
            first_session.get_messages()[-1].text,
            get_name_reply("Nora", first_session.context.get("introduction_id")),
        )

    def test_start_modes_add_one_greeting(self):
        greetings = {}
        for mode in ("direct", "introduction"):
            with self.subTest(mode=mode):
                session = ChatSession(start_mode=mode)
                controller = ChatController(session, RecordingEngine())
                greeting = controller.start_session()
                self.assertEqual(greeting.sender, "bot")
                self.assertTrue(greeting.text.strip())
                self.assertEqual(session.get_messages(), [greeting])
                self.assertEqual(controller.start_session(), greeting)
                self.assertEqual(session.get_messages(), [greeting])
                greetings[mode] = greeting.text
        self.assertNotEqual(greetings["direct"], greetings["introduction"])
        self.assertEqual(greetings, GREETINGS)

    def test_records_trimmed_user_input_then_reply_with_shared_context(self):
        session = ChatSession()
        engine = RecordingEngine()
        controller = ChatController(session, engine)
        greeting = controller.start_session()
        first_reply = controller.handle_user_message("  Hello  ")
        second_reply = controller.handle_user_message("Again")

        history = session.get_messages()
        self.assertEqual([message.sender for message in history], ["bot", "user", "bot", "user", "bot"])
        self.assertEqual(history[0], greeting)
        self.assertEqual(history[1].text, "Hello")
        self.assertEqual(history[2], first_reply)
        self.assertEqual(history[3].text, "Again")
        self.assertEqual(history[4], second_reply)
        self.assertEqual(second_reply.text, "Reply 2: Again")
        self.assertEqual(session.context.get("turn_count"), 2)
        self.assertEqual([text for text, _ in engine.calls], ["Hello", "Again"])
        self.assertTrue(all(context is session.context for _, context in engine.calls))

    def test_empty_input_does_not_record_messages_or_call_engine(self):
        session = ChatSession()
        engine = RecordingEngine()
        controller = ChatController(session, engine)
        controller.start_session()
        history = session.get_messages()

        for text in ("", "  \t\n"):
            self.assertIsNone(controller.handle_user_message(text))
        self.assertEqual(session.get_messages(), history)
        self.assertEqual(engine.calls, [])
