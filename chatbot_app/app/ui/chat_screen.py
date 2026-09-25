"""Conversation presentation; all message handling goes through the controller."""

from __future__ import annotations

from collections.abc import Callable
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

from app.chat.chat_controller import ChatController


class ChatScreen(ttk.Frame):
    """Vis og håndter én aktiv symptomkartleggingssamtale."""

    def __init__(
        self,
        master: tk.Misc,
        controller: ChatController,
        on_back: Callable[[], None],
    ) -> None:
        super().__init__(master)
        self.controller = controller
        self.input_text = tk.StringVar(master=self)

        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 16))
        ttk.Label(header, text="Dr.Oz – samtale", font=("TkDefaultFont", 18)).pack(side="left")
        ttk.Button(header, text="Tilbake", command=on_back).pack(side="right")

        self.conversation = ScrolledText(
            self, wrap="word", state="disabled", font="TkTextFont", height=16
        )
        self.conversation.pack(fill="both", expand=True)

        ttk.Label(self, text="Svar eller beskriv et symptom:").pack(anchor="w", pady=(14, 4))
        input_row = ttk.Frame(self)
        input_row.pack(fill="x")
        self.message_input = ttk.Entry(input_row, textvariable=self.input_text)
        self.message_input.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.message_input.bind("<Return>", self.send_message)
        ttk.Button(input_row, text="Send", command=self.send_message).pack(side="right")

        self.render_messages()

    def focus_input(self) -> None:
        self.message_input.focus_set()

    def send_message(self, event: tk.Event | None = None) -> str:
        response = self.controller.handle_user_message(self.input_text.get())
        if response is not None:
            self.input_text.set("")
            self.render_messages()
        self.focus_input()
        return "break"

    def render_messages(self) -> None:
        """Display the session's existing messages in their stored order."""
        self.conversation.configure(state="normal")
        self.conversation.delete("1.0", "end")
        for message in self.controller.session.get_messages():
            label = "Dr.Oz" if message.sender == "bot" else "Du"
            self.conversation.insert("end", f"{label}:\n{message.text}\n\n")
        self.conversation.configure(state="disabled")
        self.conversation.see("end")
