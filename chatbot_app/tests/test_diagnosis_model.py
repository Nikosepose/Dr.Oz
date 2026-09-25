"""Regresjonstester av pedagogiske profiler; dette er ikke klinisk validering."""

from copy import deepcopy
import json
import math
from pathlib import Path
import unittest
from unittest.mock import patch

from app.chat.chat_context import ChatContext
from app.config import MAX_QUESTIONS
from app.data.disease_loader import load_diseases, validate_dataset
from app.data.questions import get_question
from app.data.symptoms import SYMPTOM_LABELS, SYMPTOM_PATTERNS
from app.logic.diagnosis_engine import calculate_diagnoses
from app.logic.chatbot_engine import ChatbotEngine
from app.logic.question_selection import (
    calculate_information_gain, entropy, get_symptom_probability, select_next_symptom,
)


# Skrevne eksempler, ikke generert fra modellens numeriske vekter.
# Uspesifiserte symptomer er ukjente i rangeringstesten.
PROFILE_EXAMPLES = {
    "common_cold": ("runny_nose blocked_nose sneezing sore_throat", "itchy_eyes itchy_nose fever"),
    "influenza": ("fever body_aches abrupt_onset fatigue cough", ""),
    "acute_sinusitis": ("sinus_pain thick_nasal_mucus blocked_nose reduced_smell", ""),
    "tonsillitis": ("sore_throat painful_swallowing swollen_tonsils tonsil_exudate fever", "cough"),
    "acute_bronchitis": ("productive_cough cough chest_pain_coughing fatigue", "breathing_triggers itchy_eyes"),
    "asthma": ("wheezing shortness_of_breath chest_tightness breathing_triggers", "fever"),
    "allergic_rhinitis": ("itchy_nose itchy_eyes sneezing runny_nose", "fever"),
    "conjunctivitis": ("red_eyes eye_discharge gritty_eyes", "itchy_nose"),
    "otitis_media": ("ear_pain reduced_hearing fever", ""),
    "gastroenteritis": ("diarrhea vomiting nausea abdominal_cramps", "recurrent_bowel_changes"),
    "gastroesophageal_reflux": ("heartburn acid_regurgitation worse_after_meals_or_lying", ""),
    "constipation": ("constipation hard_stools straining bloating", "recurrent_bowel_changes"),
    "irritable_bowel_syndrome": ("recurrent_bowel_changes pain_relieved_defecation abdominal_cramps bloating", "fever"),
    "hemorrhoids": ("anal_itching anal_lump bright_rectal_bleeding", ""),
    "cystitis": ("dysuria urinary_frequency urinary_urgency lower_abdominal_pain", "flank_pain_waves"),
    "kidney_stone": ("flank_pain_waves pain_to_groin blood_urine nausea", ""),
    "vaginal_candidiasis": ("vaginal_itching thick_white_discharge vulval_soreness", ""),
    "migraine": ("pulsating_headache one_sided_headache light_sensitivity nausea headache_worse_activity", ""),
    "tension_headache": ("pressing_headache bilateral_headache neck_tightness", "nausea light_sensitivity"),
    "benign_positional_vertigo": ("spinning_vertigo position_triggered_vertigo brief_vertigo", ""),
    "mechanical_low_back_pain": ("low_back_pain back_pain_movement", "radiating_leg_pain leg_tingling"),
    "sciatica": ("low_back_pain radiating_leg_pain leg_tingling", ""),
    "osteoarthritis": ("joint_pain joint_stiffness activity_joint_pain", ""),
    "ankle_sprain": ("ankle_pain ankle_swelling ankle_twist bruising", ""),
    "atopic_eczema": ("itchy_skin dry_skin flexural_rash recurrent_skin_flares", "exposure_localized_rash"),
    "contact_dermatitis": ("exposure_localized_rash itchy_skin blisters rash", "recurrent_skin_flares"),
    "urticaria": ("raised_wheals changing_wheals itchy_skin", ""),
    "psoriasis": ("scaly_plaques extensor_plaques scalp_scaling", ""),
    "acne": ("pimples blackheads", ""),
    "scabies": ("night_itch finger_web_rash burrows itchy_contacts", ""),
}


class DatasetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = Path(__file__).resolve().parents[1] / "app/data/diseases.json"
        cls.raw = json.loads(path.read_text(encoding="utf-8"))

    def test_thirty_distinct_diagnoses_and_complete_symptom_space(self):
        diseases = load_diseases()
        self.assertEqual({d["id"] for d in diseases}, set(PROFILE_EXAMPLES))
        self.assertEqual(len(diseases), 30)
        self.assertGreaterEqual(len(SYMPTOM_LABELS), 75)
        self.assertEqual(set(SYMPTOM_LABELS), set(SYMPTOM_PATTERNS))
        self.assertAlmostEqual(sum(d["prior"] for d in diseases), 1)
        profiles = set()
        used = set()
        for disease, raw_disease in zip(diseases, self.raw["diseases"]):
            self.assertEqual(set(disease["symptoms"]), set(SYMPTOM_LABELS))
            self.assertTrue(disease["diagnosis"].strip())
            self.assertGreaterEqual(len(disease["characteristic_symptoms"]), 2)
            self.assertTrue(disease["source_urls"])
            profiles.add(tuple(disease["symptoms"].items()))
            used.update(raw_disease["symptoms"])
        self.assertEqual(len(profiles), 30)
        self.assertEqual(used, set(SYMPTOM_LABELS))
        for symptom in SYMPTOM_LABELS:
            self.assertTrue(SYMPTOM_PATTERNS[symptom])
            self.assertTrue(get_question(symptom).endswith("?"))

    def test_sparse_profiles_receive_background_likelihood(self):
        disease = self.raw["diseases"][0]
        omitted = next(s for s in SYMPTOM_LABELS if s not in disease["symptoms"])
        self.assertEqual(load_diseases()[0]["symptoms"][omitted], self.raw["default_symptom_probability"])

    def test_loaded_data_cannot_contaminate_another_session(self):
        diseases = load_diseases()
        diseases[0]["symptoms"]["fever"] = 0.999
        diseases[0]["characteristic_symptoms"].clear()
        self.assertNotEqual(load_diseases()[0]["symptoms"]["fever"], 0.999)
        self.assertTrue(load_diseases()[0]["characteristic_symptoms"])

    def test_invalid_probabilities_are_rejected(self):
        for invalid in (0, 1, -0.1, 1.1, True, "0.5", float("nan"), float("inf")):
            with self.subTest(value=invalid):
                data = deepcopy(self.raw)
                data["diseases"][0]["symptoms"]["fever"] = invalid
                with self.assertRaises(ValueError):
                    validate_dataset(data)

    def test_invalid_references_and_duplicate_ids_are_rejected(self):
        mutations = (
            lambda data: data["diseases"][0]["symptoms"].update(typo_symptom=0.5),
            lambda data: data["diseases"][1].update(id=data["diseases"][0]["id"]),
            lambda data: data["diseases"][0].update(characteristic_symptoms=["missing", "fever"]),
            lambda data: data["diseases"][0].update(source_urls=[]),
            lambda data: data.update(default_symptom_probability=None),
            lambda data: data["diseases"][0].update(prior=0.9),
            lambda data: data["diseases"][0].update(diagnosis=""),
        )
        for mutate in mutations:
            data = deepcopy(self.raw)
            mutate(data)
            with self.assertRaises(ValueError):
                validate_dataset(data)


class DiagnosisTests(unittest.TestCase):
    def test_each_written_symptom_combination_ranks_expected_diagnosis_first(self):
        for expected, (present, absent) in PROFILE_EXAMPLES.items():
            with self.subTest(disease=expected):
                state = dict.fromkeys(present.split(), "present")
                state.update(dict.fromkeys(absent.split(), "absent"))
                results = calculate_diagnoses(state)
                self.assertEqual(results[0]["id"], expected)
                self.assertAlmostEqual(sum(r["probability"] for r in results), 1)
                self.assertTrue(results[0]["diagnosis"])

    def test_unknown_symptoms_do_not_change_priors(self):
        results = calculate_diagnoses(dict.fromkeys(SYMPTOM_LABELS, "unknown"))
        self.assertEqual(results, calculate_diagnoses({}))
        for result in results:
            self.assertAlmostEqual(result["probability"], 1 / 30)
            self.assertEqual(result["matched_characteristic_symptoms"], [])

    def test_absence_reduces_relative_support_for_associated_disease(self):
        present = {r["id"]: r for r in calculate_diagnoses({"blackheads": "present"})}
        absent = {r["id"]: r for r in calculate_diagnoses({"blackheads": "absent"})}
        self.assertGreater(present["acne"]["probability"], absent["acne"]["probability"])

    def test_log_normalization_survives_underflow_of_raw_scores(self):
        diseases = load_diseases()
        for disease in diseases:
            disease["symptoms"] = dict.fromkeys(SYMPTOM_LABELS, 1e-10)
        results = calculate_diagnoses(dict.fromkeys(SYMPTOM_LABELS, "present"), diseases=diseases)
        self.assertTrue(all(r["score"] == 0 for r in results))
        self.assertAlmostEqual(sum(r["probability"] for r in results), 1)
        self.assertTrue(all(math.isfinite(r["probability"]) for r in results))

    def test_bad_observations_are_rejected(self):
        for state in ({"fever": "maybe"}, {"typo_symptom": "present"}):
            with self.assertRaises(ValueError):
                calculate_diagnoses(state)


class QuestionSelectionTests(unittest.TestCase):
    def test_information_gain_matches_explicit_bayes_updates(self):
        state = {"fever": "present", "cough": "absent"}
        diseases = load_diseases()
        results = calculate_diagnoses(state)
        for symptom in ("runny_nose", "dysuria", "itchy_skin"):
            with self.subTest(symptom=symptom):
                p = get_symptom_probability(symptom, results, diseases)
                expected = entropy(results) - (
                    p * entropy(calculate_diagnoses({**state, symptom: "present"}))
                    + (1 - p) * entropy(calculate_diagnoses({**state, symptom: "absent"}))
                )
                self.assertAlmostEqual(calculate_information_gain(symptom, state), expected, places=12)

    def test_selects_highest_information_without_repeating_known_or_asked(self):
        state = {"fever": "present"}
        asked = {"cough", "rash"}
        selected = select_next_symptom(state, asked)
        available = set(SYMPTOM_LABELS) - {"fever"} - asked
        self.assertIn(selected, available)
        self.assertAlmostEqual(
            calculate_information_gain(selected, state),
            max(calculate_information_gain(s, state) for s in available),
        )

    def test_one_dataset_read_per_selection(self):
        with patch("app.logic.question_selection.load_diseases", wraps=load_diseases) as loader:
            self.assertIsNotNone(select_next_symptom({}, set()))
        self.assertEqual(loader.call_count, 1)

    def test_no_questions_when_all_answered_or_asked(self):
        self.assertIsNone(select_next_symptom(dict.fromkeys(SYMPTOM_LABELS, "absent"), set()))
        self.assertIsNone(select_next_symptom({}, set(SYMPTOM_LABELS)))

    def test_identical_profiles_have_no_informative_question(self):
        diseases = load_diseases()
        for disease in diseases:
            disease["symptoms"] = dict.fromkeys(SYMPTOM_LABELS, 0.2)
        with patch("app.logic.question_selection.load_diseases", return_value=diseases):
            self.assertIsNone(select_next_symptom({}, set()))


class ModelConversationTests(unittest.TestCase):
    def test_all_thirty_profiles_can_finish_through_real_question_flow(self):
        # Fullstendige, konstruerte ja/nei-profiler. Generelle hud-/hodeplager
        # er inkludert slik at et nei ikke motsier et mer spesifikt ja.
        additions = {
            "psoriasis": "rash recurrent_skin_flares dry_skin",
            "scabies": "itchy_skin rash",
            "atopic_eczema": "rash",
            "urticaria": "rash",
            "migraine": "headache",
            "tension_headache": "headache",
        }
        for expected, (positive, _) in PROFILE_EXAMPLES.items():
            with self.subTest(disease=expected):
                present = (positive + " " + additions.get(expected, "")).split()
                if expected == "acute_bronchitis":
                    # Brystsmerter har en egen sikkerhetsavslutning. Denne
                    # profilen viser en kartlegging uten dette faresignalet.
                    present.remove("chest_pain_coughing")
                    present.append("shortness_of_breath")
                context = ChatContext()
                engine = ChatbotEngine()
                engine.process_message("Nora", context)
                reply = engine.process_message(SYMPTOM_PATTERNS[present[0]][0], context)
                asked = set()
                while context.get("stage") != "finished":
                    self.assertLess(len(asked), MAX_QUESTIONS)
                    symptom = context.get("pending_symptom")
                    self.assertIsNotNone(symptom)
                    self.assertNotIn(symptom, asked)
                    asked.add(symptom)
                    reply = engine.process_message("ja" if symptom in present else "nei", context)
                self.assertEqual(context.get("finish_reason"), "supported_match")
                best = calculate_diagnoses(context.get("patient_state"))[0]
                self.assertEqual(best["id"], expected)
                self.assertIn(best["diagnosis"], reply)


if __name__ == "__main__":
    unittest.main()
