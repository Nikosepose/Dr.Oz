"""Launch the dummy chatbot desktop application."""

import tkinter as tk

from app.ui.main_screen import MainScreen


def main() -> None:
    window = tk.Tk()
    window.title("Dummy Chatbot")
    window.geometry("760x560")
    window.minsize(480, 360)
    MainScreen(window).pack(fill="both", expand=True)
    window.mainloop()


if __name__ == "__main__":
    main()
