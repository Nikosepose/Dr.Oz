"""Samtaleflyt for avgrenset symptomkartlegging."""

from __future__ import annotations

from app.chat.chat_context import ChatContext
from app.config import MAX_QUESTIONS
from app.data.messages import (
    NAME_PROMPT,
    get_diagnosis_introduction,
    get_dr_oz_farewell,
    get_name_reply,
)
from app.data.questions import get_question
from app.logic import rules
from app.logic.conversation_state import initialize_context
from app.logic.diagnosis_engine import calculate_diagnoses
from app.logic.question_selection import select_next_symptom
from app.logic.state_scanner import parse_user_state


class ChatbotEngine:
    """Registrer observasjoner, ranger tilstander og spør om ukjente symptomer."""

    def process_message(self, text: str, context: ChatContext) -> str:
        """Behandle én melding og behold spørsmålet ved ugyldige svar."""
        initialize_context(context)
        safety_reply = rules.apply_rules(text, context)
        if safety_reply is not None:
            return safety_reply

        stage = context.get("stage")
        if stage == "finished":
            return (
                "Kartleggingen er avsluttet. "
                "Start en ny samtale fra hovedmenyen for å begynne på nytt."
            )

        if stage == "asking_name":
            name = text.strip()
            if not name:
                return NAME_PROMPT

            context.set("user_name", name)
            context.set("stage", "initial")
            return get_name_reply(name, context.get("introduction_id"))

        if stage == "initial":
            self._register_initial_observations(text, context)
        elif stage == "questions":
            answer_status = self._register_answer(text, context)
            question = context.get("pending_question")
            if answer_status == "invalid":
                return (
                    "Svar ja, nei eller vet ikke. Du kan også beskrive eller "
                    f"korrigere et symptom.\n\n{question}"
                )
            if answer_status == "updated":
                return (
                    "Opplysningene er oppdatert. Jeg venter fortsatt på svar "
                    f"på spørsmålet under.\n\n{question}"
                )
        else:
            raise ValueError(f"Ukjent samtalefase: {stage!r}")

        patient_state = context.get("patient_state")
        results = calculate_diagnoses(patient_state)

        if rules.has_reached_stop_threshold(results, patient_state):
            self._finish(context, "supported_match")
            best_match = results[0]
            name = context.get("user_name") or "der"
            return (
                f"{get_diagnosis_introduction(name)}\n\n"
                f"{best_match['diagnosis']}\n\n"
                "Dette er et forslag fra en testmodell, ikke en fastslått "
                f"diagnose.\n\n{get_dr_oz_farewell()}"
            )

        if context.get("answered_questions") >= MAX_QUESTIONS:
            return self._finish_uncertain(
                context, f"Grensen på {MAX_QUESTIONS} spørsmål er nådd."
            )

        question = self._prepare_next_question(context)
        if question is None:
            return self._finish_uncertain(
                context, "Ingen flere relevante spørsmål gjenstår."
            )
        return question

    @staticmethod
    def _finish(context: ChatContext, reason: str) -> None:
        context.set("stage", "finished")
        context.set("pending_symptom", None)
        context.set("pending_question", None)
        context.set("finish_reason", reason)

    def _finish_uncertain(
        self, context: ChatContext, reason: str
    ) -> str:
        self._finish(context, "uncertain")
        return (
            f"Kartleggingen er avsluttet. {reason} "
            "Modellen fant ikke et tilstrekkelig støttet forslag. "
            "Det er ikke grunnlag for å konkludere med en diagnose. "
            "Kontakt fastlegen hvis symptomene vedvarer eller bekymrer deg."
        )

    def _register_initial_observations(
        self, text: str, context: ChatContext
    ) -> None:
        """Registrer fritekst uten å telle den som et besvart spørsmål."""
        observations = parse_user_state(text)
        context.get("patient_state").update(observations)
        context.get("asked_symptoms").update(observations)

    def _register_answer(self, text: str, context: ChatContext) -> str:
        """Tillat fritekst og rettelser uten å miste et ubesvart spørsmål."""
        symptom = context.get("pending_symptom")
        if symptom is None:
            return "invalid"

        observations = parse_user_state(text)
        answer_state = rules.resolve_question_answer(text, symptom, observations)
        if answer_state is not None:
            observations[symptom] = answer_state
        if not observations:
            return "invalid"

        context.get("patient_state").update(observations)
        context.get("asked_symptoms").update(observations)
        if symptom not in observations:
            return "updated"

        context.set("answered_questions", context.get("answered_questions") + 1)
        context.set("pending_symptom", None)
        context.set("pending_question", None)
        return "answered"

    def _prepare_next_question(self, context: ChatContext) -> str | None:
        """Velg og klargjør neste ubesvarte spørsmål."""
        symptom = select_next_symptom(
            context.get("patient_state"), context.get("asked_symptoms")
        )
        context.set("pending_symptom", symptom)
        if symptom is None:
            context.set("pending_question", None)
            return None

        question = f"{get_question(symptom)} (ja/nei/vet ikke)"
        context.set("pending_question", question)
        context.set("stage", "questions")
        return question
