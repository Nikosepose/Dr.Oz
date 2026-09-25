"""Les, valider og kompletter de pedagogiske sykdomsprofilene."""

from copy import deepcopy
from functools import lru_cache
import json
import math
from pathlib import Path

from app.data.symptoms import SYMPTOM_LABELS


def _probability(value: object, field: str) -> float:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or not 0 < value < 1
    ):
        raise ValueError(f"{field} må være et endelig tall mellom 0 og 1.")
    return float(value)


def validate_dataset(data: dict) -> list[dict]:
    """Valider rådata og gi ALLE diagnoser samme komplette symptomrom.

    Utelatte symptomer får den eksplisitte bakgrunnsvekten. De må ikke
    ignoreres: da ville diagnoser med få registrerte symptomer få en fordel.
    """
    if not isinstance(data, dict):
        raise ValueError("Datasettet må være et JSON-objekt.")
    fallback = _probability(
        data.get("default_symptom_probability"), "default_symptom_probability"
    )
    diseases = data.get("diseases")
    if not isinstance(diseases, list) or not diseases:
        raise ValueError("Datasettet må inneholde en ikke-tom diseases-liste.")

    result = []
    identifiers = set()
    for disease in diseases:
        if not isinstance(disease, dict):
            raise ValueError("Hver diagnose må være et objekt.")
        identifier = disease.get("id")
        if not isinstance(identifier, str) or not identifier.strip():
            raise ValueError("Hver diagnose må ha en id.")
        if identifier in identifiers:
            raise ValueError(f"Duplisert diagnose-id: {identifier}")
        identifiers.add(identifier)
        if not isinstance(disease.get("name"), str) or not disease["name"].strip():
            raise ValueError(f"{identifier} mangler navn.")
        if (
            not isinstance(disease.get("diagnosis"), str)
            or not disease["diagnosis"].strip()
        ):
            raise ValueError(f"{identifier} mangler diagnosetekst.")
        prior = _probability(disease.get("prior"), f"{identifier}.prior")
        overrides = disease.get("symptoms")
        if not isinstance(overrides, dict) or not overrides:
            raise ValueError(f"{identifier} mangler symptomprofil.")
        unexpected = set(overrides) - SYMPTOM_LABELS.keys()
        if unexpected:
            raise ValueError(f"{identifier}: ukjente symptomer {sorted(unexpected)}")
        symptoms = dict.fromkeys(SYMPTOM_LABELS, fallback)
        for symptom, value in overrides.items():
            symptoms[symptom] = _probability(value, f"{identifier}.{symptom}")
        characteristic = disease.get("characteristic_symptoms")
        if (
            not isinstance(characteristic, list)
            or not all(isinstance(symptom, str) for symptom in characteristic)
            or len(characteristic) < 2
            or len(set(characteristic)) != len(characteristic)
            or any(symptom not in overrides for symptom in characteristic)
        ):
            raise ValueError(f"{identifier} må ha minst to unike kjernesymptomer i profilen.")
        sources = disease.get("source_urls")
        if not isinstance(sources, list) or not sources or not all(
            isinstance(url, str) and url.startswith("https://") for url in sources
        ):
            raise ValueError(f"{identifier} mangler HTTPS-kilder til symptomprofilen.")
        result.append({**disease, "prior": prior, "symptoms": symptoms})
    if not math.isclose(sum(d["prior"] for d in result), 1.0, abs_tol=1e-6):
        raise ValueError("Diagnosenes prior-vekter må summere til 1.")
    return result


@lru_cache(maxsize=4)
def _read_dataset(path: Path, modified_ns: int, size: int) -> list[dict]:
    # Filens versjon er del av nøkkelen, slik at dataendringer lastes på nytt.
    with path.open(encoding="utf-8") as data_file:
        return validate_dataset(json.load(data_file))


def load_diseases(data_path: Path | None = None) -> list[dict]:
    """Returner en isolert kopi; samtaler kan ikke endre den bufrede modellen."""
    path = (data_path or Path(__file__).with_name("diseases.json")).resolve()
    stat = path.stat()
    return deepcopy(_read_dataset(path, stat.st_mtime_ns, stat.st_size))
