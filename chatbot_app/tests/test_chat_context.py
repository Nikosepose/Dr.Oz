import unittest

from app.chat.chat_context import ChatContext


class ChatContextTests(unittest.TestCase):
    def test_store_retrieve_remove_and_clear(self):
        context = ChatContext()
        self.assertEqual(context.data, {})
        self.assertIsNone(context.get("missing"))
        self.assertEqual(context.get("missing", "default"), "default")

        context.set("name", "Ada")
        self.assertTrue(context.has("name"))
        self.assertEqual(context.get("name"), "Ada")
        context.set("name", "Grace")
        self.assertEqual(context.get("name"), "Grace")
        context.remove("name")
        self.assertFalse(context.has("name"))
        context.remove("missing")

        context.set("step", 1)
        context.clear()
        self.assertEqual(context.data, {})

    def test_contexts_do_not_share_data(self):
        first = ChatContext()
        second = ChatContext()
        first.set("name", "Ada")
        self.assertFalse(second.has("name"))
