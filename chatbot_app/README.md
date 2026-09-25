# Dr.Oz

En lokal Python/Tkinter-prototype for norsk symptomkartlegging. Modellen
sammenligner **30 utvalgte vanlige tilstander** med **100 symptomer og
observasjoner**, og velger oppfølgingsspørsmål som skiller alternativene.
Dette er et læringsprosjekt med syntetiske vekter, ikke et medisinsk
diagnoseverktøy. Utvalget er ikke en statistisk liste over Norges 30
hyppigste diagnoser.

## Kjør programmet

Bruk Python 3.10 eller nyere med Tkinter. Ingen pip-pakker er nødvendige.

Fra `chatbot_app` i Windows:

```powershell
.\run.cmd
```

Oppstarteren leter etter prosjektets virtuelle miljø, Windows-launcheren
`py`, Python på PATH og til slutt den tilgjengelige Codex-runtime-installasjonen.
Den installerer ingenting og endrer ikke PATH.

Med Python på PATH, fra prosjektroten:

```shell
cd chatbot_app
python main.py
```

Kontroller Tkinter med `python -m tkinter`. Hvis det mangler, installer
Tcl/Tk-komponenten som følger Python-installasjonen.

## Bruk

Velg **Start samtale** for å opprette en ny samtale. **Hva kan Dr.Oz gjøre?**
åpner en informasjonsside og oppretter ingen chattsesjon. Siden forklarer
samtaleflyten, gir brukertips og viser alle tilstandene i testmodellen.
Chatboten spør først hva du heter. Når du svarer, velges én av fem introduksjonsformuleringer
tilfeldig for samtalen. Formuleringen bruker navnet ditt og ber deg beskrive
symptomer. Én variant har en lett humoristisk tone. Det valgte alternativet og
navnet lagres bare i minnet for den aktuelle samtalen, så formuleringen endres
ikke underveis.

Beskriv symptomer, for eksempel «Jeg har kviser og hudormer» eller «Jeg har
rennende nese og nyser, men har ikke feber». Svar deretter **ja**, **nei**
eller **vet ikke** på oppfølgingsspørsmålene. Du kan også svare med fritekst
eller korrigere tidligere opplysninger, som «Jeg har ikke feber likevel».
Hvis meldingen bare omtaler et annet symptom, registreres den mens det
opprinnelige spørsmålet beholdes.

Modellen beregner mulige treff i bakgrunnen for å velge relevante
oppfølgingsspørsmål. Rangeringen og prosentvektene vises ikke i chatten.
Ved et tydelig støttet treff avsluttes kartleggingen med ett forslag, som
ikke er en medisinsk diagnose. Da brukes tilstandens diagnosetekst fra
datasettet, med forklaring, enkle råd og når det er fornuftig å kontakte
helsepersonell. Avslutningen får også en tilfeldig, åpenbart humoristisk
Dr.Oz-kommentar.

Kartleggingen avsluttes når:

- Det høyeste modelltreffet har vekt minst 0,85, margin minst 0,20 til neste
  alternativ og minst to bekreftede karakteristiske symptomer.
- 20 oppfølgingsspørsmål er besvart, eller ingen informative spørsmål gjenstår.
  Uten tilstrekkelig støtte avsluttes samtalen uttrykkelig som usikker.
- Et av de avgrensede faresignalene blir gjenkjent.

Navnesvaret og den første symptombeskrivelsen teller ikke som besvarte
oppfølgingsspørsmål.
Ugyldige svar endrer ikke tilstanden, og spørsmål med «vet ikke» gjentas
ikke. **Tilbake** går til menyen; en ny samtale får egen historikk og tilstand.
Avsluttede samtaler må startes på nytt fra menyen.

## Modell og data

Se [symptom- og diagnosegrunnlaget](app/data/DATASET.md) for alle 30
tilstander, typiske symptomkombinasjoner, kildehenvisninger og begrensninger.

`app/data/diseases.json` inneholder stabile diagnose-ID-er, norske navn,
like startvekter, symptomvekter, 2–4 karakteristiske funn og kilder.
Utelatte symptomer får den felles bakgrunnsvekten 0,03. Datainnlesingen
validerer ID-er, vekter og referanser og utvider alle profiler til samme
symptomrom, slik at diagnoser ikke belønnes for å ha få registrerte symptomer.

Rangeringen bruker naiv Bayes i logaritmisk form for numerisk stabilitet.
Ja og nei bidrar til alle profiler; ukjente svar bidrar ikke.
Spørsmålsvalget maksimerer forventet informasjonsgevinst blant ubesvarte
symptomer. Friteksttolkeren bruker norske uttrykk, ordgrenser, lokale
negasjoner og usikkerhet. Den prioriterer spesifikke uttrykk fremfor
overlappende generelle uttrykk og lar siste omtale korrigere tidligere
opplysninger.

Symptomkombinasjoner kan overlappe, og symptomer er ikke uavhengige i
virkeligheten. Modellen kjenner ikke alder, graviditet, sykehistorie,
undersøkelsesfunn eller alle mulige sykdommer. Klinisk diagnose kan derfor
ikke utledes fra modellens score.

## Avgrensede faresignaler

Før rangering kontrolleres noen tekstuttrykk for brystsmerter, alvorlige
pustevansker, talevansker/lammelser og plutselig kraftig hodepine. Bekreftede
brystsymptomer i oppfølgingsspørsmål behandles også. Negerte uttrykk skal
ikke utløse varslet. Ved treff stoppes kartleggingen og det vises råd om
113 eller 116 117 etter situasjonen.

Ordlyden bygger på Helsenorges sider om
[akutt helsehjelp](https://www.helsenorge.no/forstehjelp/ring-113/) og
[hodepine](https://www.helsenorge.no/sykdom/hodepine/).
Dette er et lite regelsett og **ikke fullstendig triage**. Manglende varsel
betyr ikke at alvorlig sykdom er utelukket.

## Struktur

```text
main.py                       Vindu og hendelsesløkke
app/
  ui/                         Meny, samtalevisning, informasjonsside og navigasjon
  chat/                       Kontroller, sesjon og samtaletilstand
  data/diseases.json          De 30 tilstandsprofilene
  data/symptoms.py            100 observasjoner, fritekstuttrykk og spørsmål
  data/disease_loader.py      Validering og komplette profiler
  data/DATASET.md             Utvalg, kilder og modellbegrensninger
  logic/state_scanner.py      Norske observasjoner, negasjon og usikkerhet
  logic/diagnosis_engine.py   Modellvekter brukt i bakgrunnen
  logic/question_selection.py Informasjonsgevinst og neste spørsmål
  logic/chatbot_engine.py     Samtaleflyt, rettelser og avslutning
  logic/rules.py              Faresignaler og krav til støttet modelltreff
  config.py                   Spørsmålsgrense og terskler
tests/                        Tester uten synlig GUI
```

Flyten er `UI -> ChatController -> ChatSession / ChatbotEngine`.
Sesjonen eier kontekst og meldinger. UI-et lager ikke svar.
Ingen nettverkstjeneste, språkmodell, database eller vedvarende historikk
brukes under kjøring; samtaledata lever bare i minnet.

## Test

Fra `chatbot_app`:

```powershell
.\run.cmd test
```

Eller med Python på PATH:

```shell
python -m unittest discover -s tests -v
```

Testene dekker datakonsistens, fritekst og negasjon, numerisk stabilitet,
spørsmålsvalg, 30 konstruerte rangeringseksempler og 30 konstruerte samtaler,
navneintroduksjonen, rettelser, spørsmålsgrensen, usikker avslutning, faresignaler,
resultatvisning og sesjonsisolasjon. Slike tester verifiserer programadferd;
de dokumenterer ikke klinisk treffsikkerhet.
