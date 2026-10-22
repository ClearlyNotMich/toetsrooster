# OWB Toetsrooster

Maakt het toetsrooster voor de **eerste kans** en de **herkansing**. Er zijn twee manieren, met precies dezelfde regels (zie [docs/REGELS.md](docs/REGELS.md)):

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

- **Instellingen** (nieuw blad): dit blad wordt de eerste keer automatisch gemaakt. Je kunt instellen:
  - studiejaar (1/2);
  - toetsduur (standaard 10 min = één slot);
  - TTV-duur (standaard 15 min), per jaar;
  - pauze van/tot.
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

1. **Werkmap openen…**: kies het Excel-bestand. Download het eerst uit OneDrive/SharePoint.
2. Kies **Eerste kans** of **Herkansing**. Controleer daarna het studiejaar, de toetsduur en de pauze.
3. **Rooster maken**: bekijk de tabbladen *Volledig rooster*, *Uitdraai studenten* en *Meldingen*.
4. **Opslaan als Excel…**: dit maakt een **nieuw** bestand met het rooster, de uitdraai en de meldingen.
   - Het origineel wordt nooit overschreven. Zo blijven de scriptknoppen daarin intact.
5. **Uitdraai studenten (PDF)…**: dit maakt een A4-lijst met alleen naam, lokaal en tijd, om op te hangen of uit te delen.

---

## Voor ontwikkelaars

- De logica staat twee keer: in `app/rooster_core.py` (Python) en in `officescripts/rooster.ts` (Office Script). De tests controleren dat beide exact dezelfde uitvoer geven.
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
