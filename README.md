# Toetsrooster

Dit programma maakt het rooster voor de vaardighedentoetsen, voor de eerste kans en de herkansing. Je vult de gegevens in en krijgt een kant-en-klaar rooster terug: een Excel-bestand, een pdf voor docenten en een pdf voor studenten.

Je kunt het op twee manieren gebruiken. Ze werken precies hetzelfde.

1. In Excel Online, met de knoppen op het eerste blad van de werkmap.
2. Met het programma Toetsrooster op je eigen computer. Dat is één bestand: dubbelklikken en het werkt. Je hoeft niets te installeren.

De volledige regels staan in [docs/REGELS.md](docs/REGELS.md).

## Wat je invult

Je werkt in een Excel-werkmap met deze bladen.

Studenten: één rij per student.
- Kolommen: studentnummer, voornaam (of roepnaam), tussenvoegsel, achternaam, klas.
- Bij wie de student niet mag: Niet inroosteren bij SB-docent, Niet inroosteren bij de vaardighedendocent. Meerdere namen scheid je met een komma of een schuine streep.
- Optioneel: TTV (Ja), Voorkeur (Ochtend, Middag, Vroeg of Laat), Opmerkingen en IsHerkanser (Ja).

Toetsdag_Kans1 en Toetsdag_Her: één rij per lokaal per toetsdag.
- Kolommen: datum, lokaal, casus, vaardigheid, beoordelaar.
- Van en Tot: wanneer de beoordelaar er is. Leeg betekent de hele dag.
- Lossen beoordelaars elkaar af, of ruilen ze van lokaal? Gebruik dan ook Beoordelaar 2 met Van 2 en Tot 2, enzovoort.
- Casus na pauze: een andere casus na de pauze (optioneel).
- Heeft een casus een speciaal lokaal nodig, zoals een keuken? Zet het tussen haakjes achter het lokaal en de casus, bijvoorbeeld C1.36 (keuken) en K3 vrouw (keuken). Het programma zet die casus dan in het goede lokaal.

Simu: één rij per simulatiepatiënt per toetsdag.
- Kolommen: datum, naam, en eventueel vanaf en tot.
- Vast lokaal (optioneel): leeg betekent dat de simu meewisselt. Ja betekent dat de simu in één lokaal blijft. Je kunt ook een lokaalnaam invullen.
- Kan spelen (optioneel): welke casussen iemand kan spelen, bijvoorbeeld vrouw, of P1, P2. Leeg betekent alles.

Instellingen: dit blad wordt vanzelf gemaakt. Hier staan onder andere:
- de begin- en eindtijd, de toetsduur (standaard 15 minuten, met TTV 20) en de pauzes;
- of simu's na elke pauze, na elke toets of nooit van lokaal wisselen;
- of lokalen evenredig worden gevuld (standaard), zodat elke beoordelaar aan de beurt komt.

Liever een lijst, zoals je het op papier opschrijft? Dat kan ook. Zet een extra blad in de werkmap met in kolom A de kopjes datum, inzet, tijden, pauzes, lokalen, casussen en simu's, en in kolom B de waarden eronder. Zie [docs/REGELS.md](docs/REGELS.md).

## Wat je terugkrijgt

- Rooster_Kans1 en Rooster_Her: het volledige rooster, per lokaal en tijd. Lege plekken staan erin als Vrije plek.
- Uitdraai_Kans1 en Uitdraai_Her: voor studenten, met alleen naam, lokaal en tijd.
- Meldingen: hoeveel studenten zijn ingeroosterd, en wat aandacht nodig heeft. Bijvoorbeeld een student zonder plek, een lokaal dat niemand krijgt, of een opmerking die het programma heeft gelezen. Kijk hier altijd even naar.
- In het programma ook een pdf voor docenten (per lokaal een pagina) en een pdf voor studenten. Vrije plekken staan daar niet op.

Gaat er iets mis in de invoer, zoals een ontbrekende kolom of een verkeerde tijd? Dan blijft het rooster ongewijzigd en staat bij Meldingen wat er mis is.

## Het programma gebruiken

### Downloaden

Ga op GitHub naar [Releases](../../releases/latest) en download bij de nieuwste versie:
- Windows: OWB-Toetsrooster.exe
- Linux: OWB-Toetsrooster-linux
- om mee te oefenen: Voorbeeld-rooster.xlsx

Op Windows kan een waarschuwing verschijnen, omdat het programma niet ondertekend is. Kies dan Meer informatie en daarna Toch uitvoeren. Op Linux maak je het bestand eerst uitvoerbaar, via Eigenschappen of met `chmod +x OWB-Toetsrooster-linux`.

### Stappen

1. Nog geen werkmap? Kies Nieuwe werkmap. Je krijgt dan een lege werkmap met alle bladen en kolommen.
2. Kies Werkmap openen en open je Excel-bestand. Download het eerst uit OneDrive of SharePoint.
3. Kies Simu's importeren om simu's over te nemen uit het overzicht Beschikbaarheid simu's. Met Simucliënten stel je per simu het vaste lokaal en Kan spelen in.
4. Kijk de instellingen na. Het programma onthoudt ze, ook na afsluiten. Heeft een werkmap andere instellingen, dan blijven die van jou actief. Op de pagina Instellingen kun je die van de werkmap overnemen.
5. Kies Eerste kans of Herkansing en klik op Rooster maken. Wissel je daarna van toets, dan wordt dat rooster meteen gemaakt. De werkmap en je instellingen blijven staan.
6. Sla het resultaat op als Excel of pdf. Je originele bestand blijft altijd ongewijzigd.

Wil je opnieuw beginnen? Kies Alles wissen onderaan de zijbalk. Het programma vergeet dan de werkmap, de geïmporteerde simu's, de instellingen en het rooster. Je Excel-bestand blijft gewoon staan.

De pagina Hulp in het programma legt hetzelfde uit.

## Excel Online

De knoppen in de werkmap gebruiken twee scripts. Die werk je zo bij (eenmalig per nieuwe versie):

1. Open de werkmap in Excel Online en ga naar Automatiseren, Alle scripts.
2. Open OWB Exam Roster Generator, selecteer alle code en vervang die door de inhoud van [OWB Exam Roster Generator.txt](OWB%20Exam%20Roster%20Generator.txt). Sla op.
3. Doe hetzelfde met OWB Retake Exam Roster Generator en [OWB Retake Exam Roster Generator.txt](OWB%20Retake%20Exam%20Roster%20Generator.txt).

Maak geen nieuwe scripts aan, maar vervang de inhoud. Dan blijven de knoppen werken.

Let op: de toetsduur voor jaar 2 staat standaard hetzelfde als jaar 1. Vul de juiste tijd in bij Instellingen.

## Voor ontwikkelaars

- De logica staat in `app/rooster_core.py` en hetzelfde nog eens in `officescripts/rooster.ts` voor Excel Online. De tests controleren dat beide precies hetzelfde rooster maken.
- Na een wijziging in `rooster.ts` maak je de scripts opnieuw met `python tools/bouw_scripts.py`.
- Een nieuwe instelling voeg je toe aan `INSTELLINGEN` in `rooster_core.py`. Het formulier in het programma, het blad Instellingen en de scripts nemen haar vanzelf over.
- Overige bestanden: `app/uitvoer.py` voor Excel, pdf, sjabloon en het beschikbaarheidsoverzicht, `app/onderdelen.py` en `app/thema.py` voor het scherm, en `app/roosterapp.py` voor het venster.
- Testen:

  ```sh
  pip install -r requirements.txt pytest
  npm ci
  QT_QPA_PLATFORM=offscreen pytest
  ```

- Bouwen: `pyinstaller roosterapp.spec`. Bij elke push naar `main` bouwt GitHub de versies voor Windows en Linux.
- Zet nooit echte werkmappen met studentgegevens in deze repository. De voorbeeldwerkmap bevat verzonnen gegevens en wordt gemaakt met `python tools/maak_voorbeeld.py`.
