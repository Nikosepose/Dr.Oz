"""Ranger modellens tilstander med numerisk stabil naiv Bayes."""

import math

from app.data.disease_loader import load_diseases
from app.data.symptoms import SYMPTOM_LABELS


def calculate_diagnoses(
    patient_state: dict[str, str], *, diseases: list[dict] | None = None
) -> list[dict]:
    """Returner relative modellvekter, ikke klinisk validerte sannsynligheter.

    Ukjente svar bidrar ikke. Både ja og nei bidrar for alle diagnoser.
    Logaritmer unngår at lange symptomlister gir numerisk underflyt.
    ``diseases`` lar spørsmålsvelgeren gjenbruke én validert innlesing.
    """
    for symptom, state in patient_state.items():
        if symptom not in SYMPTOM_LABELS:
            raise ValueError(f"Ukjent symptom: {symptom}")
        if state not in ("present", "absent", "unknown"):
            raise ValueError(f"Ugyldig tilstand for {symptom}: {state!r}")

    if diseases is None:
        diseases = load_diseases()
    if not diseases:
        raise ValueError("Modellen må inneholde minst én diagnose.")
    observed = [(s, v) for s, v in patient_state.items() if v != "unknown"]
    results = []
    for disease in diseases:
        log_score = math.log(disease["prior"])
        for symptom, state in observed:
            probability = disease["symptoms"][symptom]
            log_score += (
                math.log(probability) if state == "present"
                else math.log1p(-probability)
            )
        characteristic = disease.get("characteristic_symptoms", [])
        results.append({
            "id": disease["id"],
            "name": disease["name"],
            "diagnosis": disease["diagnosis"],
            "log_score": log_score,
            "score": math.exp(log_score),
            "characteristic_symptoms": list(characteristic),
            "matched_characteristic_symptoms": [
                symptom for symptom in characteristic
                if patient_state.get(symptom) == "present"
            ],
        })

    max_log_score = max(result["log_score"] for result in results)
    weights = [math.exp(r["log_score"] - max_log_score) for r in results]
    total = math.fsum(weights)
    for result, weight in zip(results, weights):
        result["probability"] = weight / total
        result["probability_percentage"] = result["probability"] * 100
    return sorted(results, key=lambda result: result["probability"], reverse=True)
