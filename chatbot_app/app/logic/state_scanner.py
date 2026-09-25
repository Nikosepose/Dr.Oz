"""Avgrenset, regelbasert tolking av norske symptomuttrykk.

Uttrykk må finnes i ordlisten. Lengste overlappende uttrykk vinner, og siste
omtale av et symptom bestemmer tilstanden. Negasjon og usikkerhet gjelder en
oppramsing fram til ny setning, motsetning eller eksplisitt positiv påstand.
Dette er ikke språklig eller medisinsk forståelse: historikk, andre personers
symptomer, ironi og alle former for sammensatte negasjoner tolkes ikke sikkert.
"""

from collections.abc import Mapping, Sequence
from functools import lru_cache
import re
import unicodedata
from typing import NamedTuple

from app.data.symptoms import NEGATIONS, SYMPTOM_PATTERNS


_CLAUSE_BOUNDARY = re.compile(
    r"[.!?;\n]|\b(?:men|derimot|likevel)\b"
    r"|,\s*(?=(?:jeg|har|får|opplever|kjenner|merker)\b)"
)
_ASSERTION = re.compile(r"\b(?:jeg|har|får|opplever|kjenner|merker)\b")
_FINITE_ALIAS = re.compile(
    r"(?:hoster|nyser|renner|kjenner|får|hører|kaster|kastet|spyr|spydde|"
    r"tisser|svir|klør|stråler|presser|må|piper|brenner)\b"
)
_COORDINATED_PREDICATE = re.compile(r"(?:,\s*(?:og\s+)?|\bog\s+)$")
_POST_NEGATION = re.compile(
    r"[ \t]+(?:(?:har[ \t]+)?jeg[ \t]+)?(?:ikke|aldri)\b(?![ \t]+bare\b)"
)
_UNCERTAINTY = re.compile(
    r"\b(?:"
    r"(?:vet|veit|aner)\s+ikke(?:\s+(?:helt|sikkert))?(?:\s+om)?"
    r"|(?:litt\s+)?usikker(?:\s+(?:på|om))*"
    r"|ikke\s+(?:helt\s+)?sikker(?:\s+(?:på|om))*"
    r"|kanskje|muligens|mulig(?:\s+at)?"
    r")(?:\s+(?:jeg|det))?(?:\s+(?:har|er|får|opplever))?\b"
)
_NOT_ONLY = re.compile(r"\bikke\s+bare\b")


class _Mention(NamedTuple):
    start: int
    end: int
    symptom: str


def _normalize(text: str) -> str:
    return unicodedata.normalize("NFKC", text).casefold()


@lru_cache(maxsize=1024)
def _phrase_pattern(phrase: str) -> re.Pattern[str]:
    """Match hele ord med fleksible mellomrom og bindestreker."""
    words = re.split(r"[\s\-‐‑–—]+", _normalize(phrase).strip())
    expression = r"[\s\-‐‑–—]+".join(re.escape(word) for word in words)
    return re.compile(r"(?<!\w)" + expression + r"(?!\w)")


def _find_mentions(
    text: str,
    patterns: Mapping[str, Sequence[str]],
) -> list[_Mention]:
    candidates = [
        _Mention(match.start(), match.end(), symptom)
        for symptom, phrases in patterns.items()
        for phrase in phrases
        if phrase.strip()
        for match in _phrase_pattern(phrase).finditer(text)
    ]

    # En spesifikk frase som «kløe i øynene» skal ikke også gi «kløe».
    selected: list[_Mention] = []
    for candidate in sorted(candidates, key=lambda item: (-(item.end - item.start), item.start)):
        if not any(
            candidate.start < other.end and other.start < candidate.end
            for other in selected
        ):
            selected.append(candidate)
    return sorted(selected, key=lambda item: item.start)


def _next_scope(gap: str, current: str) -> str:
    boundaries = list(_CLAUSE_BOUNDARY.finditer(gap))
    if boundaries:
        gap = gap[boundaries[-1].end():]
        current = "present"

    uncertainty = list(_UNCERTAINTY.finditer(gap))
    not_only = list(_NOT_ONLY.finditer(gap))
    protected = uncertainty + not_only
    cues = [(match.start(), "unknown") for match in uncertainty]
    cues.extend((match.start(), "present") for match in not_only)

    def is_protected(position: int) -> bool:
        return any(match.start() <= position < match.end() for match in protected)

    # En ny påstand avgrenser tidligere oppramsing, men «ikke ... har» i
    # samme uttrykk må fortsatt være negativt («tror ikke jeg har feber»).
    if any(not is_protected(match.start()) for match in _ASSERTION.finditer(gap)):
        current = "present"
    for negation in {*NEGATIONS, "verken", "hverken", "intet", "aldri"}:
        cues.extend(
            (match.start(), "absent")
            for match in _phrase_pattern(negation).finditer(gap)
            if not is_protected(match.start())
        )

    if cues:
        current = max(cues, key=lambda cue: cue[0])[1]
    return current


def parse_observations(
    text: str,
    patterns: Mapping[str, Sequence[str]],
) -> dict[str, str]:
    """Tolk en gitt ordliste med samme avgrensing og negasjon som symptomene.

    Bare omtalte uttrykk returneres. Usikre omtaler får «unknown», og en
    negasjon inne i selve uttrykket (som «får ikke puste») er en del av aliaset.
    """
    normalized = _normalize(text)
    observations: dict[str, str] = {}
    scope = "present"
    previous_end = 0
    mentions = _find_mentions(normalized, patterns)
    for index, mention in enumerate(mentions):
        gap = normalized[previous_end:mention.start]
        if (
            _FINITE_ALIAS.match(normalized[mention.start:mention.end])
            and _COORDINATED_PREDICATE.search(gap)
        ):
            # «Ingen feber og kjenner ikke lukt» begynner en ny påstand;
            # «verken feber eller hoste» fortsetter en negativ oppramsing.
            scope = "present"
        scope = _next_scope(gap, scope)
        previous_end = mention.end
        next_start = mentions[index + 1].start if index + 1 < len(mentions) else len(normalized)
        suffix = _POST_NEGATION.match(normalized[mention.end:next_start])
        if suffix:
            scope = "absent"
            previous_end += suffix.end()
        observations[mention.symptom] = scope
    return observations


def is_negated(text: str, symptom_pattern: str) -> bool:
    """Om siste hele forekomst av et uttrykk er eksplisitt benektet."""
    return parse_observations(text, {"symptom": [symptom_pattern]}).get("symptom") == "absent"


def parse_user_state(text: str) -> dict[str, str]:
    """Returner omtalte symptomer som «present», «absent» eller «unknown»."""
    return parse_observations(text, SYMPTOM_PATTERNS)
