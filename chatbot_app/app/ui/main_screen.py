"""Main menu and screen navigation for the dummy application."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from app.chat.chat_controller import ChatController
from app.chat.chat_session import ChatSession
from app.logic.chatbot_engine import ChatbotEngine
from app.ui.chat_screen import ChatScreen


class MainScreen(ttk.Frame):
    """Create a fresh conversation whenever either menu option is selected."""

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master, padding=24)
        self.chat_screen: ChatScreen | None = None
        self.menu = ttk.Frame(self)
        self.menu.pack(fill="both", expand=True)

        ttk.Label(self.menu, text="Dummy Chatbot", font=("TkDefaultFont", 22)).pack(
            pady=(50, 12)
        )
        ttk.Label(self.menu, text="Welcome to the chatbot demo.").pack(pady=(0, 28))
        ttk.Button(
            self.menu,
            text="Start Chat",
            command=lambda: self.start_chat("direct"),
        ).pack(pady=6, ipadx=16, ipady=6)
        ttk.Button(
            self.menu,
            text="What can this chatbot do?",
            command=lambda: self.start_chat("introduction"),
        ).pack(pady=6, ipadx=16, ipady=6)

    def start_chat(self, start_mode: str) -> None:
        # This is the composition point for swapping in your own engine later.
        session = ChatSession(start_mode=start_mode)
        controller = ChatController(session, ChatbotEngine())
        controller.start_session()

        self.menu.pack_forget()
        if self.chat_screen is not None:
            self.chat_screen.destroy()
        self.chat_screen = ChatScreen(self, controller, on_back=self.show_main)
        self.chat_screen.pack(fill="both", expand=True)
        self.chat_screen.focus_input()

    def show_main(self) -> None:
        """Discard the active chat view and return to the two start options."""
        if self.chat_screen is not None:
            self.chat_screen.destroy()
            self.chat_screen = None
        self.menu.pack(fill="both", expand=True)
