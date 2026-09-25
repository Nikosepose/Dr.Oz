import unittest
from copy import deepcopy
from unittest.mock import patch

from app.chat.chat_context import ChatContext
from app.config import MAX_QUESTIONS
from app.data.messages import (
    DIAGNOSIS_INTRODUCTIONS,
    DR_OZ_FAREWELLS,
    INITIAL_PROMPT,
    INTRODUCTION_VARIANTS,
    NAME_PROMPT,
    get_name_reply,
)
from app.data.questions import get_question
from app.data.disease_loader import load_diseases
from app.data.symptoms import SYMPTOM_LABELS
from app.logic.chatbot_engine import ChatbotEngine
from app.logic.conversation_state import initialize_context
from app.logic.rules import has_reached_stop_threshold


class ChatbotEngineTests(unittest.TestCase):
    def setUp(self):
        self.engine = ChatbotEngine()
        self.context = ChatContext()
        self.engine.process_message("Nora", self.context)

    def set_pending(self, symptom):
        initialize_context(self.context)
        self.context.set("stage", "questions")
        self.context.set("pending_symptom", symptom)
        self.context.set("pending_question", f"{get_question(symptom)} (ja/nei/vet ikke)")

    def test_initial_description_registers_symptoms_without_counting_question(self):
        reply = self.engine.process_message("Jeg har feber", self.context)
        state = self.context.get("patient_state")
        self.assertEqual(set(state), set(SYMPTOM_LABELS))
        self.assertEqual(state["fever"], "present")
        self.assertTrue(all(v == "unknown" for k, v in state.items() if k != "fever"))
        self.assertEqual(self.context.get("asked_symptoms"), {"fever"})
        self.assertEqual(self.context.get("answered_questions"), 0)
        self.assertEqual(self.context.get("stage"), "questions")
        symptom = self.context.get("pending_symptom")
        self.assertIn(symptom, SYMPTOM_LABELS)
        self.assertNotEqual(symptom, "fever")
        self.assertEqual(
            self.context.get("pending_question"),
            f"{get_question(symptom)} (ja/nei/vet ikke)",
        )
        self.assertIn(self.context.get("pending_question"), reply)
        self.assertNotIn("testmodellen", reply)
        self.assertNotIn("%", reply)

    def test_invalid_answer_preserves_context(self):
        initial_reply = self.engine.process_message("Hei", self.context)
        before = deepcopy(self.context.data)
        question = self.context.get("pending_question")
        reply = self.engine.process_message("usammenhengende svar", self.context)
        self.assertEqual(self.context.data, before)
        self.assertIn(question, initial_reply)
        self.assertIn(question, reply)
        self.assertIn("Svar ja, nei eller vet ikke.", reply)

    def test_unknown_answers_finish_at_limit_without_repeated_questions(self):
        self.engine.process_message("Hei", self.context)
        seen = set()
        for _ in range(MAX_QUESTIONS):
            symptom = self.context.get("pending_symptom")
            self.assertIn(symptom, SYMPTOM_LABELS)
            self.assertNotIn(symptom, seen)
            seen.add(symptom)
            reply = self.engine.process_message("  VET IKKE  ", self.context)
        self.assertEqual(len(seen), MAX_QUESTIONS)
        self.assertEqual(self.context.get("asked_symptoms"), seen)
        self.assertTrue(all(v == "unknown" for v in self.context.get("patient_state").values()))
        self.assertEqual(self.context.get("answered_questions"), MAX_QUESTIONS)
        self.assertEqual(self.context.get("stage"), "finished")
        self.assertEqual(self.context.get("finish_reason"), "uncertain")
        self.assertIsNone(self.context.get("pending_symptom"))
        self.assertIsNone(self.context.get("pending_question"))
        self.assertIn("ikke grunnlag for å konkludere", reply)
        self.assertNotIn("passer best med", reply)
        self.assertNotIn("Foreløpige treff", reply)

    def test_all_no_never_produces_a_supported_diagnosis(self):
        self.engine.process_message("Hei", self.context)
        for _ in range(MAX_QUESTIONS):
            reply = self.engine.process_message("nei", self.context)
            if self.context.get("stage") == "finished":
                break
        self.assertEqual(self.context.get("finish_reason"), "uncertain")
        self.assertNotIn("passer best med", reply)
        self.assertNotIn("Foreløpige treff", reply)

    def test_correction_of_other_symptom_keeps_pending_question(self):
        self.engine.process_message("Jeg har feber", self.context)
        before_question = self.context.get("pending_question")
        before_symptom = self.context.get("pending_symptom")
        reply = self.engine.process_message("Jeg har ikke feber likevel", self.context)
        self.assertEqual(self.context.get("patient_state")["fever"], "absent")
        self.assertEqual(self.context.get("pending_symptom"), before_symptom)
        self.assertEqual(self.context.get("pending_question"), before_question)
        self.assertEqual(self.context.get("answered_questions"), 0)
        self.assertIn(before_question, reply)

    def test_free_text_can_answer_pending_question_and_add_observations(self):
        self.set_pending("fever")
        self.engine.process_message("Jeg har feber og hoste", self.context)
        self.assertEqual(self.context.get("patient_state")["fever"], "present")
        self.assertEqual(self.context.get("patient_state")["cough"], "present")
        self.assertEqual(self.context.get("answered_questions"), 1)
        self.assertNotEqual(self.context.get("pending_symptom"), "fever")

    def test_yes_prefix_and_free_text_are_both_registered(self):
        self.set_pending("fever")
        self.engine.process_message("Ja, og jeg har hoste", self.context)
        self.assertEqual(self.context.get("patient_state")["fever"], "present")
        self.assertEqual(self.context.get("patient_state")["cough"], "present")
        self.assertEqual(self.context.get("answered_questions"), 1)

    def test_finished_conversation_does_not_restart(self):
        initialize_context(self.context)
        self.context.set("stage", "finished")
        before = deepcopy(self.context.data)
        reply = self.engine.process_message("Jeg har feber", self.context)
        self.assertEqual(self.context.data, before)
        self.assertIn("Start en ny samtale", reply)

    def test_exhausted_symptoms_end_with_uncertainty(self):
        initialize_context(self.context)
        self.context.get("asked_symptoms").update(SYMPTOM_LABELS)
        reply = self.engine.process_message("Hei", self.context)
        self.assertEqual(self.context.get("finish_reason"), "uncertain")
        self.assertIn("Ingen flere relevante spørsmål", reply)

    def test_strong_model_match_with_characteristic_evidence_can_finish(self):
        intro = DIAGNOSIS_INTRODUCTIONS[0]
        farewell = DR_OZ_FAREWELLS[0]
        acne_text = next(
            disease["diagnosis"]
            for disease in load_diseases()
            if disease["id"] == "acne"
        )
        with (
            patch(
                "app.logic.chatbot_engine.get_diagnosis_introduction",
                return_value=intro.format(name="Nora"),
            ) as diagnosis_intro,
            patch(
                "app.logic.chatbot_engine.get_dr_oz_farewell",
                return_value=farewell,
            ) as dr_oz_farewell,
        ):
            reply = self.engine.process_message(
                "Jeg har kviser og hudormer", self.context
            )
        self.assertEqual(self.context.get("finish_reason"), "supported_match")
        self.assertIn(intro.format(name="Nora"), reply)
        self.assertIn(acne_text, reply)
        self.assertTrue(reply.endswith(farewell))
        self.assertIn("ikke en fastslått diagnose", reply)
        diagnosis_intro.assert_called_once_with("Nora")
        dr_oz_farewell.assert_called_once_with()

    def test_red_flags_intercept_before_diagnosis_ranking(self):
        for text in (
            "Jeg har brystsmerter",
            "Jeg har kraftige pustevansker",
            "Jeg klarer ikke å puste",
            "Jeg har plutselig kraftig hodepine",
            "Jeg har plutselige talevansker",
            "Jeg har lammelse i armen",
            "Jeg har ikke hoste, men jeg får ikke puste",
        ):
            with self.subTest(text=text):
                context = ChatContext()
                with patch("app.logic.chatbot_engine.calculate_diagnoses") as rank:
                    reply = self.engine.process_message(text, context)
                rank.assert_not_called()
                self.assertIn("113", reply)
                self.assertEqual(context.get("finish_reason"), "safety")
                self.assertIsNone(context.get("pending_question"))

    def test_negated_red_flags_do_not_intercept(self):
        for text in (
            "Jeg har ikke brystsmerter",
            "Ingen brystsmerter eller talevansker",
            "Jeg har ikke plutselig kraftig hodepine",
            "Jeg har ikke kraftige pustevansker",
        ):
            with self.subTest(text=text):
                context = ChatContext()
                self.engine.process_message("Nora", context)
                reply = self.engine.process_message(text, context)
                self.assertNotEqual(context.get("finish_reason"), "safety")
                self.assertNotIn("Ring 113", reply)

    def test_red_flag_after_negated_symptom_still_intercepts(self):
        reply = self.engine.process_message(
            "Jeg har ikke brystsmerter, men jeg har plutselig kraftig hodepine",
            self.context,
        )
        self.assertIn("Ring 113", reply)
        self.assertEqual(self.context.get("finish_reason"), "safety")

    def test_yes_to_chest_symptom_intercepts(self):
        for answer in ("ja", "j", "Ja!", "ja, også feber"):
            with self.subTest(answer=answer):
                self.context = ChatContext()
                self.set_pending("chest_pain_coughing")
                reply = self.engine.process_message(answer, self.context)
                self.assertIn("116 117", reply)
                self.assertEqual(self.context.get("finish_reason"), "safety")

    def test_explicitly_negated_chest_pain_overrides_yes_for_safety(self):
        self.set_pending("chest_pain_coughing")
        reply = self.engine.process_message(
            "Ja, men jeg har ikke smerter i brystet når jeg hoster", self.context
        )
        self.assertNotEqual(self.context.get("finish_reason"), "safety")
        self.assertNotIn("Ring 113", reply)

    def test_red_flags_are_handled_even_after_conversation_finished(self):
        initialize_context(self.context)
        self.context.set("stage", "finished")
        reply = self.engine.process_message("Nå har jeg brystsmerter", self.context)
        self.assertIn("113", reply)
        self.assertEqual(self.context.get("finish_reason"), "safety")


class NameIntroductionTests(unittest.TestCase):
    def test_name_is_trimmed_and_saved_before_symptom_processing(self):
        context = ChatContext()
        initialize_context(context)
        self.assertEqual(context.get("stage"), "asking_name")
        patient_state = deepcopy(context.get("patient_state"))

        with (
            patch("app.logic.chatbot_engine.parse_user_state") as parse,
            patch("app.logic.chatbot_engine.calculate_diagnoses") as rank,
            patch("app.logic.chatbot_engine.select_next_symptom") as select,
        ):
            reply = ChatbotEngine().process_message("  Nora  ", context)

        self.assertEqual(
            reply, get_name_reply("Nora", context.get("introduction_id"))
        )
        self.assertIn("Nora", reply)
        self.assertIn(INITIAL_PROMPT, reply)
        self.assertEqual(context.get("user_name"), "Nora")
        self.assertEqual(context.get("stage"), "initial")
        self.assertEqual(context.get("patient_state"), patient_state)
        self.assertEqual(context.get("asked_symptoms"), set())
        self.assertEqual(context.get("answered_questions"), 0)
        self.assertIsNone(context.get("pending_symptom"))
        self.assertIsNone(context.get("pending_question"))
        parse.assert_not_called()
        rank.assert_not_called()
        select.assert_not_called()

    def test_empty_name_keeps_name_question_and_context(self):
        context = ChatContext()
        initialize_context(context)
        before = deepcopy(context.data)
        engine = ChatbotEngine()

        for text in ("", "  \t\n"):
            with self.subTest(text=text):
                reply = engine.process_message(text, context)
                self.assertIn(NAME_PROMPT, reply)
                self.assertEqual(context.data, before)

    def test_all_five_variants_include_name_and_symptom_prompt(self):
        self.assertEqual(len(INTRODUCTION_VARIANTS), 5)
        for introduction_id in INTRODUCTION_VARIANTS:
            with self.subTest(introduction_id=introduction_id):
                reply = get_name_reply("Ada", introduction_id)
                self.assertIn("Ada", reply)
                self.assertIn(INITIAL_PROMPT, reply)
        self.assertIn(
            "stetoskop",
            get_name_reply("Ada", "playful").casefold(),
        )


class StopAndPresentationTests(unittest.TestCase):
    def test_high_relative_weight_requires_two_characteristic_symptoms(self):
        results = [{
            "probability": .99,
            "characteristic_symptoms": ["fever", "cough"],
        }, {"probability": .01}]
        for state in (
            {}, {"fever": "absent", "cough": "absent"},
            {"fever": "present", "cough": "unknown"},
        ):
            self.assertFalse(has_reached_stop_threshold(results, state))
        self.assertTrue(has_reached_stop_threshold(
            results, {"fever": "present", "cough": "present"}
        ))

    def test_relative_weight_below_threshold_is_insufficient(self):
        self.assertFalse(has_reached_stop_threshold([{
            "probability": .84,
            "matched_characteristic_symptoms": ["fever", "cough"],
        }]))
        self.assertFalse(has_reached_stop_threshold([]))

    def test_chat_does_not_display_ranked_model_results(self):
        context = ChatContext()
        engine = ChatbotEngine()
        engine.process_message("Nora", context)
        reply = engine.process_message("Jeg har feber", context)
        self.assertEqual(reply, context.get("pending_question"))
        self.assertNotIn("Foreløpige treff", reply)
        self.assertNotIn("modellvekt", reply)
        self.assertNotIn("%", reply)
