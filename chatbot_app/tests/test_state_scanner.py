import unittest

from app.logic.state_scanner import is_negated, parse_observations, parse_user_state


class StateScannerTests(unittest.TestCase):
    def test_case_and_punctuation(self):
        self.assertEqual(
            parse_user_state("FEber! Jeg HOSTER, og har vondt i hodet."),
            {"fever": "present", "cough": "present", "headache": "present"},
        )

    def test_alias_does_not_match_inside_another_word(self):
        self.assertEqual(parse_user_state("hostesaft, febermåler og hodepinetabletter"), {})

    def test_flexible_whitespace_and_hyphens(self):
        self.assertEqual(
            parse_observations("Jeg har sår hals og vondt-i   hodet", {
                "throat": ["sår hals"], "headache": ["vondt i hodet"],
            }),
            {"throat": "present", "headache": "present"},
        )

    def test_longest_overlapping_alias_wins(self):
        self.assertEqual(
            parse_observations("Kløe i øynene og pulserende hodepine", {
                "itching": ["kløe"],
                "headache": ["hodepine"],
                "itchy_eyes": ["kløe i øynene"],
                "pulsating_headache": ["pulserende hodepine"],
            }),
            {"itchy_eyes": "present", "pulsating_headache": "present"},
        )

    def test_negation_covers_a_list(self):
        self.assertEqual(
            parse_user_state("Jeg har ingen feber, hodepine eller hoste."),
            {"fever": "absent", "headache": "absent", "cough": "absent"},
        )
        self.assertEqual(
            parse_user_state("Verken feber eller hoste"),
            {"fever": "absent", "cough": "absent"},
        )

    def test_contrast_ends_negation(self):
        self.assertEqual(
            parse_user_state("Ikke feber, men hoste."),
            {"fever": "absent", "cough": "present"},
        )

    def test_sentence_ends_negation(self):
        for separator in (". ", "; ", "\n"):
            with self.subTest(separator=separator):
                self.assertEqual(
                    parse_user_state(f"Ikke feber{separator}Hoste"),
                    {"fever": "absent", "cough": "present"},
                )
        self.assertEqual(
            parse_user_state("Feber\nIkke hoste"),
            {"fever": "present", "cough": "absent"},
        )

    def test_new_assertion_ends_negation(self):
        for text in (
            "Jeg har ikke feber og jeg hoster",
            "Ingen feber, og har hoste",
            "Ikke feber. Jeg har hoste",
        ):
            with self.subTest(text=text):
                self.assertEqual(parse_user_state(text), {"fever": "absent", "cough": "present"})

    def test_negation_before_a_verb_is_still_negative(self):
        for text in ("Jeg tror ikke jeg har feber", "Uten at jeg har feber"):
            with self.subTest(text=text):
                self.assertEqual(parse_user_state(text), {"fever": "absent"})

    def test_negation_after_symptom_does_not_leak_to_next_assertion(self):
        self.assertEqual(
            parse_user_state("Jeg hoster ikke og har feber"),
            {"cough": "absent", "fever": "present"},
        )
        self.assertEqual(
            parse_user_state("Feber har jeg ikke, men hodepine"),
            {"fever": "absent", "headache": "present"},
        )

    def test_predicate_alias_after_negative_observation_is_positive(self):
        self.assertEqual(
            parse_user_state("Ingen feber og kjenner ikke lukt"),
            {"fever": "absent", "reduced_smell": "present"},
        )
        self.assertEqual(
            parse_user_state("Jeg har ingen feber og hoster opp slim"),
            {"fever": "absent", "productive_cough": "present"},
        )
        self.assertEqual(
            parse_user_state("Jeg verken nyser eller hoster"),
            {"sneezing": "absent", "cough": "absent"},
        )

    def test_last_mention_wins_across_aliases(self):
        self.assertEqual(parse_user_state("Ingen feber tidligere, men nå har jeg feber"), {"fever": "present"})
        self.assertEqual(parse_user_state("Jeg hoster, men har ikke hoste nå"), {"cough": "absent"})

    def test_uncertainty_is_unknown_instead_of_absent(self):
        for text in (
            "Jeg vet ikke om jeg har feber",
            "Jeg er usikker på om jeg har feber",
            "Jeg er ikke helt sikker på om jeg har feber",
            "Kanskje feber",
        ):
            with self.subTest(text=text):
                self.assertEqual(parse_user_state(text), {"fever": "unknown"})

    def test_uncertainty_covers_list_until_assertion(self):
        self.assertEqual(
            parse_user_state("Vet ikke om jeg har feber eller hoste, men jeg har hodepine"),
            {"fever": "unknown", "cough": "unknown", "headache": "present"},
        )
        self.assertEqual(
            parse_user_state("Jeg vet ikke hva dette er, jeg har feber"),
            {"fever": "present"},
        )

    def test_not_only_is_positive(self):
        self.assertEqual(
            parse_user_state("Jeg har ikke bare feber, men også hoste"),
            {"fever": "present", "cough": "present"},
        )

    def test_negation_word_is_not_a_substring(self):
        self.assertEqual(parse_user_state("Jeg drikker vann og har feber"), {"fever": "present"})

    def test_negation_inside_alias_is_part_of_the_symptom(self):
        self.assertEqual(
            parse_observations("Jeg får ikke puste", {"breathing": ["får ikke puste"]}),
            {"breathing": "present"},
        )
        self.assertEqual(
            parse_observations("Ingen feber, men jeg får ikke puste", {
                "fever": ["feber"], "breathing": ["får ikke puste"],
            }),
            {"fever": "absent", "breathing": "present"},
        )

    def test_specific_catalog_aliases_do_not_add_general_symptoms(self):
        self.assertEqual(
            parse_user_state("Jeg hoster opp slim, har kløe i øynene og utslett mellom fingrene."),
            {"productive_cough": "present", "itchy_eyes": "present", "finger_web_rash": "present"},
        )

    def test_catalog_aliases_can_contain_an_intrinsic_negation(self):
        self.assertEqual(parse_user_state("Jeg kjenner ikke lukt"), {"reduced_smell": "present"})
        self.assertEqual(parse_user_state("Jeg får ikke bæsjet"), {"constipation": "present"})

    def test_temperature_without_fever_is_not_a_positive_observation(self):
        self.assertEqual(parse_user_state("Jeg målte temperaturen til 36,8 grader"), {})

    def test_public_negation_helper_uses_last_occurrence_and_boundaries(self):
        self.assertTrue(is_negated("Feber i går, men ingen feber nå", "feber"))
        self.assertFalse(is_negated("Ingen feber tidligere. Nå har jeg feber", "feber"))
        self.assertFalse(is_negated("Ingen febermåler", "feber"))
        self.assertFalse(is_negated("Vet ikke om jeg har feber", "feber"))

    def test_unrecognized_text_has_no_observations(self):
        self.assertEqual(parse_user_state("Hei, kan du hjelpe meg?"), {})


if __name__ == "__main__":
    unittest.main()
