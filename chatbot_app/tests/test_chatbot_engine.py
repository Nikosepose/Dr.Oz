import unittest
from unittest.mock import patch

from app.chat.chat_context import ChatContext
from app.logic import rules
from app.logic.chatbot_engine import ChatbotEngine


class ChatbotEngineTests(unittest.TestCase):
    def test_placeholder_rules_allow_dummy_fallback(self):
        context = ChatContext()
        self.assertIsNone(rules.apply_rules("Hello", context))
        self.assertEqual(
            ChatbotEngine().process_message("Hello", context),
            "Dummy chatbot received: Hello",
        )

    def test_rule_response_overrides_fallback(self):
        context = ChatContext()
        with patch.object(rules, "apply_rules", return_value="Rule reply") as rule:
            response = ChatbotEngine().process_message("Hello", context)
        self.assertEqual(response, "Rule reply")
        rule.assert_called_once_with("Hello", context)
