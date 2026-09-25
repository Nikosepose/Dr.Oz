import unittest
from unittest.mock import patch

from app.chat.chat_context import ChatContext
from app.data.messages import (
    DIAGNOSIS_INTRODUCTIONS,
    DR_OZ_FAREWELLS,
    INTRODUCTION_VARIANTS,
    choose_introduction_id,
    get_diagnosis_introduction,
    get_dr_oz_farewell,
    get_name_reply,
)
from app.logic.conversation_state import initialize_context


class IntroductionVariantTests(unittest.TestCase):
    def test_selector_can_choose_each_of_the_five_stable_variant_ids(self):
        for introduction_id in INTRODUCTION_VARIANTS:
            with self.subTest(introduction_id=introduction_id):
                with patch("app.data.messages.random.choice", return_value=introduction_id):
                    self.assertEqual(choose_introduction_id(), introduction_id)

    def test_selected_variant_is_kept_for_the_entire_name_introduction(self):
        context = ChatContext()
        with patch(
            "app.logic.conversation_state.choose_introduction_id",
            return_value="playful",
        ) as choose:
            initialize_context(context)
            initialize_context(context)
        self.assertEqual(choose.call_count, 1)
        self.assertEqual(context.get("introduction_id"), "playful")
        self.assertEqual(
            get_name_reply("Nora", context.get("introduction_id")),
            get_name_reply("Nora", "playful"),
        )

    def test_diagnosis_intro_and_farewell_cover_all_configured_variants(self):
        self.assertEqual(len(DIAGNOSIS_INTRODUCTIONS), 5)
        self.assertEqual(len(DR_OZ_FAREWELLS), 10)
        for introduction in DIAGNOSIS_INTRODUCTIONS:
            with self.subTest(introduction=introduction):
                with patch("app.data.messages.random.choice", return_value=introduction):
                    self.assertEqual(
                        get_diagnosis_introduction("Nikolai"), introduction.format(name="Nikolai")
                    )
        for farewell in DR_OZ_FAREWELLS:
            with self.subTest(farewell=farewell):
                with patch("app.data.messages.random.choice", return_value=farewell):
                    self.assertEqual(get_dr_oz_farewell(), farewell)


if __name__ == "__main__":
    unittest.main()
