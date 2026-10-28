# Toetsrooster

Met dit programma maak je het rooster voor de vaardighedentoetsen, zowel voor de eerste kans als voor de herkansing. Je zet de studenten, toetsdagen en simu's in een Excel-werkmap en het programma maakt daar een rooster van: een Excel-bestand, een pdf voor docenten en een pdf voor studenten.

Je kunt het op twee manieren gebruiken, met bij allebei dezelfde uitkomst:

- in Excel Online, via de knoppen op het eerste blad van de werkmap;
- met het programma Toetsrooster op je eigen computer. Dat is één los bestand dat je zonder installatie start.

## De werkmap invullen

### Studenten

Per student één rij, met studentnummer, voornaam (of roepnaam), tussenvoegsel, achternaam en klas.

In Niet inroosteren bij SB-docent en Niet inroosteren bij de vaardighedendocent zet je bij wie een student niet terecht mag komen. Meerdere namen scheid je met een komma of een schuine streep.

TTV (Ja), Voorkeur (Ochtend, Middag, Vroeg of Laat), Opmerkingen en IsHerkanser (Ja) mag je invullen, maar het hoeft niet.

### Toetsdag_Kans1 en Toetsdag_Her

Per toetsdag één rij per lokaal, met datum, lokaal, casus, vaardigheid en beoordelaar.

Met Van en Tot geef je aan wanneer de beoordelaar er is. Laat je ze leeg, dan is dat de hele dag. Wisselen beoordelaars elkaar af of ruilen ze van lokaal, gebruik dan Beoordelaar 2 met Van 2 en Tot 2 (en zo verder). Wordt er na de pauze een andere casus gespeeld, dan zet je die in Casus na pauze.

Sommige casussen moeten in een bepaald lokaal, bijvoorbeeld een keuken. Zet dat tussen haakjes achter zowel het lokaal als de casus, zoals C1.36 (keuken) en K3 vrouw (keuken), dan koppelt het programma ze aan elkaar.

### Simu

Per toetsdag één rij per simulatiepatiënt: datum, naam en eventueel vanaf en tot. Laat je de datum leeg, dan geldt de rij voor elke toetsdag.

Vast lokaal bepaalt of een simu van lokaal wisselt. Leeg betekent dat de simu meewisselt, Ja dat de simu in één lokaal blijft. Je kunt ook meteen een lokaalnaam invullen. In Kan spelen zet je welke casussen iemand kan spelen, bijvoorbeeld vrouw of P1, P2. Leeg is alles.

### Instellingen

Dit blad maakt het programma zelf aan. Hier staan onder meer de begin- en eindtijd, de pauzes en de toetsduur (standaard 15 minuten, 20 met TTV). Je stelt hier ook in of simu's na elke pauze, na elke toets of nooit van lokaal wisselen, en of de lokalen evenredig gevuld worden zodat iedere beoordelaar studenten krijgt. Dat laatste staat standaard aan.

Werk je liever met een lijstje, zoals je het op papier zou opschrijven, dan kan dat ook. Voeg een blad toe met in kolom A de kopjes datum, inzet, tijden, pauzes, lokalen, casussen en simu's, en in kolom B de waarden. Staat zo'n lijst in de werkmap, dan gebruikt het programma die in plaats van het blad Toetsdag, en gaan de tijden en pauzes uit de lijst voor de instellingen. Hoe dat precies werkt staat in [docs/REGELS.md](docs/REGELS.md).

## Wat eruit komt

- Rooster_Kans1 en Rooster_Her: het complete rooster per lokaal en tijd. Lege plekken staan erin als Vrije plek.
- Uitdraai_Kans1 en Uitdraai_Her: de versie voor studenten, met alleen naam, lokaal en tijd.
- Meldingen: hoeveel studenten er zijn ingeroosterd en waar je naar moet kijken, zoals een student zonder plek, een lokaal waar niemand in komt of een opmerking die het programma heeft meegenomen. Loop dit blad elke keer even door.
- Vanuit het programma ook een pdf voor docenten (één pagina per lokaal per dag) en een voor studenten, allebei zonder de vrije plekken.

Klopt er iets niet in de invoer, bijvoorbeeld een ontbrekende kolom of een tijd die niet te lezen is, dan blijft het rooster zoals het was. Wat er mis is lees je bij Meldingen.

## Het programma gebruiken

### Downloaden

Download de nieuwste versie via [Releases](../../releases/latest):

- OWB-Toetsrooster.exe voor Windows
- OWB-Toetsrooster-linux voor Linux
- Voorbeeld-rooster.xlsx als je eerst wilt oefenen

Het programma is niet ondertekend, dus Windows geeft mogelijk een waarschuwing. Klik dan op Meer informatie en daarna op Toch uitvoeren. Op Linux maak je het bestand eerst uitvoerbaar, via Eigenschappen of met `chmod +x OWB-Toetsrooster-linux`.

### Een rooster maken

1. Heb je nog geen werkmap, kies dan Nieuwe werkmap. Je krijgt een lege werkmap met alle bladen en kolommen, die meteen geopend wordt. Vul hem in Excel in en open hem daarna opnieuw.
2. Open je Excel-bestand met Werkmap openen. Staat het in OneDrive of SharePoint, download het dan eerst.
3. Met Simu's importeren haal je de simu's uit het overzicht Beschikbaarheid simu's. Bij Simucliënten stel je per simu het vaste lokaal en Kan spelen in. Deze wijzigingen bewaar je pas als je het resultaat met Excel opslaan wegschrijft.
4. Loop de instellingen na. De eerste keer neemt het programma de instellingen uit de werkmap over. Daarna onthoudt het je eigen instellingen, ook na afsluiten, en een werkmap met andere instellingen overschrijft ze niet. Wil je toch de instellingen uit de werkmap gebruiken, dan neem je die over op de pagina Instellingen.
5. Kies Eerste kans of Herkansing en klik op Rooster maken. Wissel je daarna naar de andere toets, dan wordt dat rooster direct gemaakt. Je werkmap en instellingen blijven staan.
6. Sla het resultaat op als Excel of pdf. Excel opslaan maakt altijd een nieuw bestand, met ook je instellingen in het blad Instellingen. Aan je originele bestand verandert niets.

Met Alles wissen, onderaan de zijbalk, begin je opnieuw. Het programma vergeet dan de werkmap, de geïmporteerde simu's, de instellingen en het rooster. Je Excel-bestand zelf blijft bestaan.

Dezelfde uitleg staat ook op de pagina Hulp in het programma.

## Excel Online bijwerken

De knoppen in de werkmap draaien op twee scripts. Bij een nieuwe versie werk je die één keer bij:

1. Open de werkmap in Excel Online en ga naar Automatiseren > Alle scripts.
2. Open OWB Exam Roster Generator, selecteer alle code en vervang die door de inhoud van [OWB Exam Roster Generator.txt](OWB%20Exam%20Roster%20Generator.txt). Sla op.
3. Doe hetzelfde met OWB Retake Exam Roster Generator en [OWB Retake Exam Roster Generator.txt](OWB%20Retake%20Exam%20Roster%20Generator.txt).

Vervang alleen de inhoud en maak geen nieuwe scripts aan, anders werken de knoppen niet meer.

Let op: de toetsduur voor jaar 2 staat standaard gelijk aan die van jaar 1. Pas dat aan bij Instellingen.

## Voor ontwikkelaars

- De roosterlogica zit in `app/rooster_core.py`, met een kopie in `officescripts/rooster.ts` voor Excel Online. De tests controleren dat beide hetzelfde rooster opleveren.
- Heb je `rooster.ts` aangepast, maak de scripts dan opnieuw met `python tools/bouw_scripts.py`.
- Een nieuwe instelling voeg je toe aan `INSTELLINGEN` in `rooster_core.py`. Het formulier in het programma, het blad Instellingen en de scripts pakken die vanzelf op.
- `app/uitvoer.py` doet Excel, pdf, het sjabloon en het beschikbaarheidsoverzicht. `app/onderdelen.py` en `app/thema.py` zijn voor het scherm, `app/roosterapp.py` voor het venster.
- Testen:

  ```sh
  pip install -r requirements.txt pytest
  npm ci
  QT_QPA_PLATFORM=offscreen pytest
  ```

- Bouwen doe je met `pyinstaller roosterapp.spec`. Bij elke push naar `main` bouwt GitHub zelf de versies voor Windows en Linux.
- Zet nooit echte werkmappen met studentgegevens in deze repository. De voorbeeldwerkmap bevat verzonnen gegevens.
