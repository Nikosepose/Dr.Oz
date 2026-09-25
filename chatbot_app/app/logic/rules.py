"""Avgrenset sikkerhetsfilter og krav til avslutning i testmodellen."""

from __future__ import annotations

import re

from app.chat.chat_context import ChatContext
from app.config import MIN_CHARACTERISTIC_SYMPTOMS, STOP_MARGIN, STOP_PROBABILITY
from app.data.questions import ANSWER_MAPPING
from app.logic.state_scanner import parse_observations, parse_user_state


# En liten språkregel kan ikke utelukke alvorlig sykdom. Kilder:
# https://www.helsenorge.no/forstehjelp/ring-113/
# https://www.helsenorge.no/sykdom/hodepine/
RED_FLAG_PATTERNS = {
    "chest_pain": [
        "brystsmerter", "brystsmerte", "smerter i brystet", "smerte i brystet",
        "vondt i brystet", "trykk i brystet", "klemmende smerter i brystet",
    ],
    "severe_breathing": [
        "får ikke puste", "klarer ikke å puste", "kan ikke puste",
        "alvorlige pustevansker", "store pustevansker", "kraftige pustevansker",
        "svært tungpustet", "veldig tungpustet", "pustevansker i hvile",
        "svært vanskelig å puste", "veldig vanskelig å puste",
    ],
    "stroke_signs": [
        "plutselige talevansker", "plutselig talevansker", "talevansker",
        "utydelig tale", "problemer med å snakke", "problemer med å prate",
        "klarer ikke å snakke", "klarer ikke å smile", "skjevt smil",
        "ansiktslammelse", "lammelse i armen", "lammelser i armen",
        "lammelse i ansiktet", "lammelser i ansiktet",
        "plutselig svakhet i armen", "plutselig svakhet på en side",
        "klarer ikke å løfte armen", "klarer ikke å løfte armene",
    ],
    "thunderclap": [
        "plutselig kraftig hodepine", "plutselig sterk hodepine",
        "plutselig intens hodepine", "plutselig og kraftig hodepine",
        "plutselig og sterk hodepine", "plutselig og svært kraftig hodepine",
        "plutselig veldig vondt i hodet", "verste hodepinen i livet",
        "verste hodepine i livet", "eksplosiv hodepine", "lynaktig hodepine",
    ],
}


def apply_rules(text: str, context: ChatContext) -> str | None:
    """Avbryt rangering når en av de avgrensede faresignalreglene treffer."""
    observations = parse_observations(text, RED_FLAG_PATTERNS)
    present = {key for key, state in observations.items() if state == "present"}
    # Bruk samme svarfortolkning som samtaleflyten, også for j og ja, ...
    symptom_observations = parse_user_state(text)
    pending = context.get("pending_symptom")
    chest_symptoms = {"chest_pain_coughing", "chest_tightness"}
    chest_confirmed = any(
        symptom_observations.get(symptom) == "present" for symptom in chest_symptoms
    ) or (
        pending in chest_symptoms
        and resolve_question_answer(text, pending, symptom_observations) == "present"
    )
    if chest_confirmed and observations.get("chest_pain") not in {"absent", "unknown"}:
        present.add("chest_pain")

    if not present:
        return None

    context.set("stage", "finished")
    context.set("pending_symptom", None)
    context.set("pending_question", None)
    context.set("finish_reason", "safety")
    if present - {"chest_pain"}:
        return (
            "Du beskriver et mulig faresignal. Ring 113 nå ved alvorlige "
            "pustevansker, nye talevansker eller lammelser, eller plutselig "
            "kraftig hodepine. Jeg avslutter symptomkartleggingen; dette må "
            "vurderes av helsepersonell."
        )
    return (
        "Smerter eller trykk i brystet må vurderes av helsepersonell. "
        "Ring 113 hvis smertene varer mer enn fem minutter, er sterke, "
        "eller du samtidig er tungpustet eller føler deg akutt dårlig. "
        "Ellers: kontakt legevakt på 116 117 dersom hjelpen ikke kan vente "
        "eller fastlegen er utilgjengelig. Jeg avslutter symptomkartleggingen."
    )


def resolve_question_answer(
    text: str, symptom: str | None, observations: dict[str, str]
) -> str | None:
    """Felles fortolkning av korte svar, svarprefiks og eksplisitte rettelser."""
    if symptom in observations:
        return observations[symptom]
    answer = text.casefold().strip().rstrip(".! ")
    if answer in ANSWER_MAPPING:
        return ANSWER_MAPPING[answer]
    prefix = re.match(r"^(ja|j|nei|ne|n|vet ikke|ukjent)\s*[,!.:;]", answer)
    return ANSWER_MAPPING[prefix.group(1)] if prefix else None


def has_reached_stop_threshold(
    results: list[dict],
    patient_state: dict[str, str] | None = None,
) -> bool:
    """Krev et tydelig modelltreff med minst to bekreftede kjennetegn."""
    if not results or results[0]["probability"] < STOP_PROBABILITY:
        return False

    best = results[0]
    runner_up = results[1]["probability"] if len(results) > 1 else 0.0
    if best["probability"] - runner_up < STOP_MARGIN:
        return False

    if patient_state is None:
        matched = set(best.get("matched_characteristic_symptoms", ()))
    else:
        matched = {
            symptom
            for symptom in best.get("characteristic_symptoms", ())
            if patient_state.get(symptom) == "present"
        }
    return len(matched) >= MIN_CHARACTERISTIC_SYMPTOMS
