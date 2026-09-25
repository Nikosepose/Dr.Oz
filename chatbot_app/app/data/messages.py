"""Tekster og stabile introduksjonsvarianter for samtalen."""

from __future__ import annotations

import random


NAME_PROMPT = "Først lurer jeg på hva du heter?"

INITIAL_PROMPT = (
    "Fortell litt om hvordan du har det, "
    "og hvilke symptomer du har lagt merke til."
)

# Variasjonen er avgrenset til introduksjonen. Nøkkelen lagres per samtale,
# slik at den samme formuleringen brukes dersom navnesvaret må gjentas.
INTRODUCTION_VARIANTS = {
    "warm": (
        "Hyggelig å møte deg, {name}! Jeg er klar til å lytte. "
        "{initial_prompt}"
    ),
    "calm": (
        "Takk, {name}. Ta den tiden du trenger, og beskriv gjerne plagene "
        "slik du opplever dem. {initial_prompt}"
    ),
    "curious": (
        "Fint å ha deg her, {name}. Vi starter enkelt og tar én ting om "
        "gangen. {initial_prompt}"
    ),
    "structured": (
        "Hei, {name}. Jeg stiller noen korte oppfølgingsspørsmål etterpå "
        "for å få oversikt. {initial_prompt}"
    ),
    "playful": (
        "Hyggelig å møte deg, {name}! Jeg har ikke stetoskop, men jeg er "
        "ganske god til å stille spørsmål. {initial_prompt}"
    ),
}

DIAGNOSIS_INTRODUCTIONS = (
    "Nå tror jeg vi har funnet et godt spor, {name}.",
    "Dette symptommønsteret peker ganske tydelig i én retning, {name}.",
    "Da har jeg et forslag til deg, {name}.",
    "Vi har kommet frem til et mulig svar, {name}.",
    "Jeg har sammenlignet svarene dine, {name}, og dette ser mest sannsynlig ut.",
)

# Avslutningene er Dr.Oz-humor og holdes adskilt fra den medisinske informasjonen.
DR_OZ_FAREWELLS = (
    "Dr.Oz anbefaler foreløpig en kopp te og kvantekrystaller som kan kjøpes på nettsiden våres.",
    "Min faktura for konsultasjonen er nå sendt til din addresse.",
    "Du kan betale meg i form av en gullmynt, eller vipps.",
    "Resepten på måneskinn og magnetarmbånd er dessverre tom.",
    "Du skylder meg ikke mye, men siden dette var en omfattende konsultasjon kan du gi en vipps på ett lite laken.",
    "Jeg selger vidundermidler, kanskje du er interessert i å se på vår nettbutikk. Om du er heldig får du produktet med signaturen min.",
    "Det beste tilskuddet i dag er fortsatt vanlig sunn fornuft, samt Dr.Oz mineralvann.",
    "Krystallkulen min er på service, men kan merke din shakra energi er på plass.",
    "Betaling kan gjøres i form av crypto eller kontanter i en konvolutt.",
    "Dr.Oz tar nå en velfortjent pause for å kalibrere pendelen sin.",
)


def choose_introduction_id() -> str:
    """Velg én av de fem variantene ved starten av en ny samtale."""
    return random.choice(tuple(INTRODUCTION_VARIANTS))


def get_name_reply(name: str, introduction_id: str) -> str:
    """Lag introduksjonen etter navnesvaret fra den lagrede varianten."""
    try:
        template = INTRODUCTION_VARIANTS[introduction_id]
    except KeyError as error:
        raise ValueError(f"Ukjent introduksjonsvariant: {introduction_id!r}") from error
    return template.format(name=name, initial_prompt=INITIAL_PROMPT)


def get_diagnosis_introduction(name: str) -> str:
    """Lag en kort, navngitt innledning til den endelige vurderingen."""
    return random.choice(DIAGNOSIS_INTRODUCTIONS).format(name=name)


def get_dr_oz_farewell() -> str:
    """Velg én tydelig humoristisk, ikke-kommersiell Dr.Oz-avslutning."""
    return random.choice(DR_OZ_FAREWELLS)


GREETINGS = {
    "direct": (
        "Hei! Dr.Oz er en læringsprototype og kan ikke stille en medisinsk "
        f"diagnose. {NAME_PROMPT}"
    ),
    "introduction": (
        "Hei! Jeg er Dr.Oz, en læringsprototype for symptomkartlegging. "
        "Jeg registrerer symptomer fra beskrivelsen din, stiller "
        "oppfølgingsspørsmål og viser resultater fra en enkel testmodell "
        "med 30 tilstander. Resultatene er forslag, ikke medisinske "
        f"diagnoser.\n\n{NAME_PROMPT}"
    ),
}
