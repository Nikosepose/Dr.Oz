"""Hovedmeny og navigasjon for Dr.Oz."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from app.chat.chat_controller import ChatController
from app.chat.chat_session import ChatSession
from app.logic.chatbot_engine import ChatbotEngine
from app.ui.chat_screen import ChatScreen
from app.ui.info_screen import InfoScreen


class MainScreen(ttk.Frame):
    """Vis menyen og opprett bare en chat når brukeren starter en samtale."""

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master, padding=24)
        self.chat_screen: ChatScreen | None = None
        self.info_screen: InfoScreen | None = None
        self.menu = ttk.Frame(self)
        self.menu.pack(fill="both", expand=True)

        ttk.Label(self.menu, text="Dr.Oz", font=("TkDefaultFont", 22)).pack(
            pady=(50, 12)
        )
        ttk.Label(
            self.menu,
            text="Symptomkartlegging – læringsprototype, ikke medisinsk diagnose",
            wraplength=410,
            justify="center",
        ).pack(pady=(0, 28))
        ttk.Button(
            self.menu,
            text="Start samtale",
            command=self.start_chat,
        ).pack(pady=6, ipadx=16, ipady=6)
        ttk.Button(
            self.menu,
            text="Hva kan Dr.Oz gjøre?",
            command=self.show_info,
        ).pack(pady=6, ipadx=16, ipady=6)

    def start_chat(self) -> None:
        # Sett sammen en ny sesjon, kontroller og samtalemotor.
        session = ChatSession()
        controller = ChatController(session, ChatbotEngine())
        controller.start_session()

        self.menu.pack_forget()
        if self.chat_screen is not None:
            self.chat_screen.destroy()
        self.chat_screen = ChatScreen(self, controller, on_back=self.show_main)
        self.chat_screen.pack(fill="both", expand=True)
        self.chat_screen.focus_input()

    def show_info(self) -> None:
        """Åpne informasjonssiden uten å opprette en chattsesjon."""
        self.menu.pack_forget()
        if self.info_screen is not None:
            self.info_screen.destroy()
        self.info_screen = InfoScreen(self, on_back=self.show_main)
        self.info_screen.pack(fill="both", expand=True)

    def show_main(self) -> None:
        """Lukk aktiv visning og gå tilbake til hovedmenyen."""
        if self.chat_screen is not None:
            self.chat_screen.destroy()
            self.chat_screen = None
        if self.info_screen is not None:
            self.info_screen.destroy()
            self.info_screen = None
        self.menu.pack(fill="both", expand=True)
