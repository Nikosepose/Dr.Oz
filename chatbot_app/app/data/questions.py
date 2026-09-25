"""Spørsmålsmaler og gyldige svar til symptomkartlegging."""

from app.data.symptoms import SYMPTOM_QUESTIONS


QUESTION_TEMPLATES = [
    "Har du {symptom}?",
    "Har du problemer med {symptom}?",
    "Opplever du {symptom}?",
    "Har du merket noe til {symptom}?",
    "Føler du deg plaget av {symptom}?",
]


def get_question(symptom: str) -> str:
    """Returner et presist og deterministisk spørsmål for symptomet."""
    return SYMPTOM_QUESTIONS[symptom]


ANSWER_MAPPING = {
    # Present
    "ja": "present",
    "j": "present",
    "jepp": "present",
    "japp": "present",
    "yes": "present",
    "y": "present",
    "stemmer": "present",
    "riktig": "present",
    "korrekt": "present",
    "absolutt": "present",
    "definitivt": "present",
    "selvfølgelig": "present",
    "har det": "present",
    "det har jeg": "present",
    "jeg har det": "present",
    "opplever det": "present",
    "jeg opplever det": "present",

    # Absent
    "nei": "absent",
    "ne": "absent",
    "n": "absent",
    "no": "absent",
    "nope": "absent",
    "ikke": "absent",
    "stemmer ikke": "absent",
    "feil": "absent",
    "ikke i det hele tatt": "absent",
    "har ikke": "absent",
    "det har jeg ikke": "absent",
    "jeg har ikke det": "absent",
    "opplever ikke det": "absent",
    "jeg opplever ikke det": "absent",

    # Unknown
    "vet ikke": "unknown",
    "jeg vet ikke": "unknown",
    "veit ikke": "unknown",
    "jeg veit ikke": "unknown",
    "ukjent": "unknown",
    "usikker": "unknown",
    "jeg er usikker": "unknown",
    "ikke sikker": "unknown",
    "ikke helt sikker": "unknown",
    "aner ikke": "unknown",
    "jeg aner ikke": "unknown",
    "vanskelig å si": "unknown",
    "kan ikke si": "unknown",
    "kanskje": "unknown",
    "muligens": "unknown",
    "mulig": "unknown",
    "tror det": "unknown",
    "tror ikke det": "unknown",
    "ikke som jeg vet": "unknown",
    "ikke som jeg vet om": "unknown",
}
