"""Velg spørsmål som forventes å skille de gjenstående profilene best."""

import math

from app.data.disease_loader import load_diseases
from app.data.symptoms import SYMPTOM_LABELS
from app.logic.diagnosis_engine import calculate_diagnoses


def entropy(results: list[dict]) -> float:
    """Shannon-entropi for en normalisert modellfordeling."""
    return -math.fsum(
        r["probability"] * math.log2(r["probability"])
        for r in results if r["probability"] > 0
    )


def _binary_entropy(probability: float) -> float:
    if probability <= 0 or probability >= 1:
        return 0.0
    return -(
        probability * math.log2(probability)
        + (1 - probability) * math.log2(1 - probability)
    )


def get_symptom_probability(
    symptom: str, current_results: list[dict], diseases: list[dict]
) -> float:
    by_id = {disease["id"]: disease for disease in diseases}
    return math.fsum(
        result["probability"] * by_id[result["id"]]["symptoms"][symptom]
        for result in current_results
    )


def _information_gain(
    symptom: str, results: list[dict], by_id: dict[str, dict]
) -> float:
    pairs = [
        (result["probability"], by_id[result["id"]]["symptoms"][symptom])
        for result in results
    ]
    probability_present = math.fsum(weight * p for weight, p in pairs)
    # I(diagnose; svar) = H(svar) - E[H(svar | diagnose)]. Dette er lik
    # entropireduksjonen fra to Bayes-oppdateringer, uten gjentatt fil-I/O.
    gain = _binary_entropy(probability_present) - math.fsum(
        weight * _binary_entropy(p) for weight, p in pairs
    )
    return max(0.0, gain)


def calculate_information_gain(symptom: str, patient_state: dict[str, str]) -> float:
    """Forventet informasjonsverdi ved et ja/nei-svar på et ukjent symptom."""
    if symptom not in SYMPTOM_LABELS:
        raise ValueError(f"Ukjent symptom: {symptom}")
    diseases = load_diseases()
    results = calculate_diagnoses(patient_state, diseases=diseases)
    if patient_state.get(symptom, "unknown") != "unknown":
        return 0.0
    return _information_gain(symptom, results, {d["id"]: d for d in diseases})


def select_next_symptom(
    patient_state: dict[str, str], asked_symptoms: set[str]
) -> str | None:
    """Velg ett informativt symptom; besvarte/ukjente svar gjentas ikke."""
    diseases = load_diseases()
    results = calculate_diagnoses(patient_state, diseases=diseases)
    by_id = {disease["id"]: disease for disease in diseases}
    best_symptom = None
    best_gain = 1e-12
    for symptom in SYMPTOM_LABELS:
        if patient_state.get(symptom, "unknown") != "unknown" or symptom in asked_symptoms:
            continue
        gain = _information_gain(symptom, results, by_id)
        if gain > best_gain:
            best_symptom, best_gain = symptom, gain
    return best_symptom
