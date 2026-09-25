"""Opprett arbeidsdataene for én samtale."""

from app.chat.chat_context import ChatContext
from app.data.messages import choose_introduction_id
from app.data.symptoms import SYMPTOM_LABELS


def initialize_context(context: ChatContext) -> None:
    """Opprett starttilstanden én gang per samtale."""
    if context.has("stage"):
        return

    patient_state = {
        symptom: "unknown"
        for symptom in SYMPTOM_LABELS
    }

    context.set("patient_state", patient_state)
    context.set("asked_symptoms", set())
    context.set("pending_symptom", None)
    context.set("pending_question", None)
    context.set("answered_questions", 0)
    context.set("user_name", None)
    context.set("introduction_id", choose_introduction_id())
    context.set("stage", "asking_name")
