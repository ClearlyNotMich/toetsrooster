# OWB Toetsrooster

Maakt het toetsrooster voor de **eerste kans** en de **herkansing**. Je vult de gegevens in: studenten, tijdslots, beoordelaars en simucliënten. Je krijgt een kant-en-klaar rooster terug, als Excel-werkmap en als PDF om te printen of te publiceren. Er is geen roostermaker meer nodig die het met de hand doet.

Er zijn twee manieren, met precies dezelfde regels (zie [docs/REGELS.md](docs/REGELS.md)):

1. **In Excel Online** met de knoppen op het eerste blad (Office Scripts, geen VBA).
2. Met het **programma OWB-Toetsrooster**: één bestand, dubbelklikken, niets installeren.

---

## 1. Excel Online: scripts bijwerken (eenmalig)

De knoppen op het blad *Studenten* verwijzen naar de scripts in je OneDrive. Vervang de **inhoud** van die scripts. Maak geen nieuwe scripts aan, dan blijven de knoppen werken.

1. Open de werkmap in Excel Online en ga naar **Automatiseren** → **Alle scripts**.
2. Open **OWB Exam Roster Generator** en selecteer alle code (Ctrl+A).
3. Plak de volledige inhoud van [`OWB Exam Roster Generator.txt`](OWB%20Exam%20Roster%20Generator.txt) en kies **Script opslaan**.
4. Doe hetzelfde met **OWB Retake Exam Roster Generator** en [`OWB Retake Exam Roster Generator.txt`](OWB%20Retake%20Exam%20Roster%20Generator.txt).
   - Bestaat dit script nog niet, maak het aan met precies deze naam.
   - Koppel het daarna via **⋯ → Knop toevoegen** aan een knop.
5. Klik op de knop **Run OWB Exam Roster Generator**.

### Wat er verandert in de werkmap

- **Instellingen** (nieuw blad): dit blad wordt de eerste keer automatisch gemaakt. Je kunt onder andere instellen:
  - studiejaar en toetsduur per jaar (standaard 10 min = één slot; TTV 15 min);
  - pauze en casus na de pauze;
  - waar TTV-studenten komen;
  - herkansingsregels (Voorkeur/Verplicht/Maakt niet uit);
  - sortering en datum op de uitdraai;
  - alle bladnamen.

  Zie de tabel in [docs/REGELS.md](docs/REGELS.md#instellingen). De app schrijft zijn instellingen bij *Excel opslaan* naar hetzelfde blad, zodat de knoppen in Excel Online daarna dezelfde regels gebruiken.
- **Rooster_Kans1 / Rooster_Her**:
  - het volledige rooster voor docenten, gesorteerd op datum → lokaal → tijd;
  - de kolommen *Lokaal*, *Casus* en *Eindtijd*.
- **Uitdraai_Kans1 / Uitdraai_Her** (nieuw): voor studenten, met **alleen naam, lokaal en tijd**. Er staat geen studentnummer, casus, beoordelaar of simucliënt op.
- **Meldingen** (nieuw): hier staat hoeveel studenten zijn ingeroosterd. Ook waarschuwingen staan hier, zoals:
  - studenten die niet passen;
  - een herkanser die toch dezelfde beoordelaar heeft;
  - fouten in de invoer.

  Bij een fout blijft het rooster ongewijzigd.
- **Slots_Kans1 / Slots_Her**: voeg desgewenst de kolom **Casus na pauze** toe. Slots na de pauze krijgen dan die casus.
- **Studenten**: de eerste kans vult nu de juiste kolommen *EersteDatum*, *EersteTijd*, *EersteBeoordelaar* en *EersteCasus*.
  - Het oude script schreef één kolom te vroeg, waardoor er datums in *IsHerkanser* stonden. Maak die cellen leeg en zet `Ja` bij de herkansers.
  - Zolang dat niet is gebeurd, verschijnt er een waarschuwing.

> Let op: vul bij **Toetsduur jaar 2** de echte tijd voor jaar 2 in. Standaard staat er 10/15 min, net als in jaar 1, omdat de juiste waarde voor jaar 2 niet bekend was.

---

## 2. Programma OWB-Toetsrooster (Windows en Linux)

### Downloaden

Op GitHub → **Actions** → laatste geslaagde run **Bouw programma's** → *Artifacts*:

- **OWB-Toetsrooster-Windows**: `OWB-Toetsrooster.exe`
- **OWB-Toetsrooster-Linux**: `OWB-Toetsrooster`

Pak de zip uit. Er hoeft niets anders geïnstalleerd te worden: Python en Qt zitten in het bestand.

- **Windows**:
  1. Dubbelklik op het bestand.
  2. Waarschuwt SmartScreen, kies dan **Meer informatie → Toch uitvoeren**. Het programma is niet ondertekend.
- **Linux**: maak het bestand eenmalig uitvoerbaar met *Eigenschappen → Uitvoerbaar*, of `chmod +x OWB-Toetsrooster`. Dubbelklik daarna.
- Het eerste opstarten duurt een paar seconden, omdat het bestand zichzelf uitpakt.

### Gebruik

1. Nog geen werkmap? Klik in de zijbalk op **Nieuw sjabloon…**. Je krijgt dan een lege werkmap met de juiste bladen en kolommen om in te vullen.
2. **Werkmap openen…**: kies het Excel-bestand. Download het eerst uit OneDrive/SharePoint.
3. Controleer de pagina **Instellingen**. Deze wordt gevuld vanuit het blad Instellingen van de werkmap. *Standaardwaarden* zet alles terug.
4. Kies op de pagina **Rooster** voor **Eerste kans** of **Herkansing** en klik op **Rooster maken**.
   - De kaarten tonen hoeveel studenten zijn ingeroosterd, en of er waarschuwingen zijn of studenten zonder plek.
   - Details staan op het tabblad *Meldingen*.
5. Exporteer:
   - **Excel opslaan…**: een **nieuw** bestand met het rooster, de uitdraai, de meldingen en de instellingen. Het origineel wordt nooit overschreven, zodat de scriptknoppen daarin intact blijven.
   - **PDF voor docenten…**: per lokaal en dag een A4-pagina (liggend) met tijd, student, casus, beoordelaar en simucliënt.
   - **PDF voor studenten…**: alleen naam, lokaal en tijd, om te publiceren of op te hangen.

De pagina **Hulp** in de app legt dezelfde stappen uit.

---

## Voor ontwikkelaars

- Opbouw van de app:
  - `app/rooster_core.py`: logica en de lijst met instellingen;
  - `app/uitvoer.py`: Excel, PDF en sjabloon;
  - `app/thema.py`: kleuren en stijl, naar shadcn/ui *neutral*;
  - `app/onderdelen.py`: UI-onderdelen, waaronder het instellingenformulier, dat zichzelf opbouwt uit de instellingenlijst;
  - `app/roosterapp.py`: het venster.
- Een nieuwe instelling voeg je toe in `INSTELLINGEN` in `rooster_core.py`. Gebruik haar daarna in `maak_rooster`, en in `officescripts/rooster.ts` via `txt("sleutel")`. Formulier, blad Instellingen en scripts volgen dan vanzelf.
- De logica staat twee keer: in `app/rooster_core.py` (Python) en in `officescripts/rooster.ts` (Office Script). De tests controleren dat beide exact dezelfde uitvoer geven, ook bij afwijkende instellingen.
- Na een wijziging in `rooster.ts` maak je de twee `.txt`-scripts opnieuw met `python tools/bouw_scripts.py`.
- Testen:

  ```sh
  pip install -r requirements.txt pytest
  npm ci
  QT_QPA_PLATFORM=offscreen pytest
  ```

  - De Office Scripts worden gecontroleerd met TypeScript 4.0.3, de versie van Excel Online.
  - Daarna draaien ze tegen een nagebootste werkmap.
- Lokaal bouwen: `pip install pyinstaller && pyinstaller roosterapp.spec` maakt `dist/`. Bij een push naar `main` bouwt GitHub Actions automatisch voor Windows en Linux.
- Zet **nooit** echte werkmappen met studentgegevens in deze repository. `.gitignore` laat alleen code en `voorbeeld/` toe. De voorbeeldwerkmap bevat verzonnen gegevens (`python tools/maak_voorbeeld.py`).
