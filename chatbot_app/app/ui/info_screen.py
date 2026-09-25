"""Informasjonsside for Dr.Oz uten en aktiv chattsesjon."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from tkinter import ttk

from app.data.disease_loader import load_diseases


def get_supported_disease_names() -> list[str]:
    """Returner navnene fra datasettet slik at informasjonssiden alltid er oppdatert."""
    return [disease["name"] for disease in load_diseases()]


class InfoScreen(ttk.Frame):
    """Vis flyt, brukerveiledning og tilstandene i testmodellen."""

    def __init__(self, master: tk.Misc, on_back: Callable[[], None]) -> None:
        super().__init__(master)

        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 12))
        ttk.Label(header, text="Hva kan Dr.Oz gjøre?", font=("TkDefaultFont", 18)).pack(
            side="left"
        )
        ttk.Button(header, text="Tilbake", command=on_back).pack(side="right")

        canvas = tk.Canvas(self, highlightthickness=0, borderwidth=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        content = ttk.Frame(canvas, padding=(2, 2, 14, 14))
        content_window = canvas.create_window((0, 0), window=content, anchor="nw")
        content.bind(
            "<Configure>",
            lambda _event: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.bind(
            "<Configure>",
            lambda event: canvas.itemconfigure(content_window, width=event.width),
        )

        self._add_overview(content)
        self._add_flow(content)
        self._add_guidance(content)
        self._add_diseases(content)

    @staticmethod
    def _section(parent: ttk.Frame, title: str) -> ttk.LabelFrame:
        section = ttk.LabelFrame(parent, text=title, padding=12)
        section.pack(fill="x", pady=(0, 10))
        return section

    def _add_overview(self, content: ttk.Frame) -> None:
        section = self._section(content, "Om Dr.Oz")
        ttk.Label(
            section,
            justify="left",
            wraplength=660,
            text=(
                "Dr.Oz er en læringsprototype for symptomkartlegging. "
                "Den bruker svarene dine til å velge relevante spørsmål fra "
                "et avgrenset datasett. Den kan ikke stille en medisinsk diagnose."
            ),
        ).pack(anchor="w")

    def _add_flow(self, content: ttk.Frame) -> None:
        section = self._section(content, "Slik foregår en samtale")
        steps = (
            ("1", "Skriv navnet ditt", "Dr.Oz bruker navnet ditt i introduksjonen."),
            ("2", "Beskriv plagene", "Fortell med egne ord hva du kjenner på."),
            ("3", "Svar på oppfølginger", "Svar ja, nei eller vet ikke. Du kan korrigere tidligere svar."),
            ("4", "Få et forslag", "Ved nok støtte får du ett forslag og råd fra den aktuelle profilen."),
        )
        for number, title, description in steps:
            row = ttk.Frame(section)
            row.pack(fill="x", pady=3)
            ttk.Label(row, text=number, width=3, font=("TkDefaultFont", 10, "bold")).pack(
                side="left", anchor="n"
            )
            text = ttk.Frame(row)
            text.pack(side="left", fill="x", expand=True)
            ttk.Label(text, text=title, font=("TkDefaultFont", 10, "bold")).pack(anchor="w")
            ttk.Label(text, text=description, wraplength=610, justify="left").pack(anchor="w")

    def _add_guidance(self, content: ttk.Frame) -> None:
        section = self._section(content, "Tips for gode svar")
        ttk.Label(
            section,
            justify="left",
            wraplength=660,
            text=(
                "Beskriv konkrete symptomer, for eksempel «Jeg har feber og hoste». "
                "Hvis noe har endret seg, kan du skrive det direkte, som «Jeg har "
                "ikke feber likevel». Fritekst, ja, nei og vet ikke fungerer alle "
                "som svar. Ved akutte eller alvorlige plager skal du kontakte "
                "helsepersonell, ikke vente på kartleggingen."
            ),
        ).pack(anchor="w")

    def _add_diseases(self, content: ttk.Frame) -> None:
        diseases = get_supported_disease_names()
        section = self._section(content, f"Tilstander i testmodellen ({len(diseases)})")
        columns = 3
        for column in range(columns):
            section.columnconfigure(column, weight=1)
        rows = (len(diseases) + columns - 1) // columns
        for index, name in enumerate(diseases):
            column = index // rows
            row = index % rows
            ttk.Label(section, text=f"• {name}", wraplength=200, justify="left").grid(
                row=row, column=column, sticky="w", padx=(0, 12), pady=2
            )
        ttk.Label(
            section,
            text=(
                "Dette er de eneste tilstandene modellen sammenligner. "
                "Listen er ikke en oversikt over alle mulige årsaker til symptomer."
            ),
            wraplength=660,
            justify="left",
        ).grid(row=rows, column=0, columnspan=columns, sticky="w", pady=(12, 0))
