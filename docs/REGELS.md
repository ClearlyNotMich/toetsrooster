# Hoe het rooster gemaakt wordt

Het programma en de scripts in Excel Online volgen precies dezelfde regels. Hieronder staat hoe het werkt.

## De dag

Het programma maakt de tijden van de dag zelf, uit de instellingen: begintijd, eindtijd, toetsduur, wisseltijd en pauzes. Standaard begint er elke 20 minuten een student (15 minuten toets en 5 minuten wissel), van 09:40 tot 17:00, met pauzes om 11:15, 13:00 en 15:15. Dat zijn 17 plekken per lokaal.

Een gewone toets valt nooit in een pauze. Een toets met TTV mag doorlopen in de pauze die erna komt.

De toetsduur was eerst 10 minuten. Die is aangepast aan het echte rooster. Dat de TTV-toets 20 minuten duurt, is een aanname. Controleer die.

## Lokalen en beoordelaars

Elke rij in het blad Toetsdag is een lokaal op een dag, met een casus, een vaardigheid en een of meer beoordelaars. De beoordelaar en de casus blijven de hele dag in dat lokaal.

Bij elke beoordelaar horen de kolommen Van en Tot. Leeg betekent de hele dag. Komen er meer beoordelaars in één lokaal, dan gebruik je Beoordelaar 2 met Van 2 en Tot 2, enzovoort. Per toets kiest het programma de eerste beoordelaar die dan de hele toets kan doen.

| Lokaal | Beoordelaar | Van | Tot | Beoordelaar 2 | Van 2 | Tot 2 |
|---|---|---|---|---|---|---|
| C1.39 | Fien | | 13:00 | Hans | 13:30 | |
| A | Ann | | 13:00 | Bram | 13:00 | |
| B | Bram | | 13:00 | Ann | 13:00 | |

In dit voorbeeld neemt Hans na de lunch het over van Fien. Ann en Bram ruilen om 13:00 van lokaal. Staat iemand op hetzelfde moment in twee lokalen, dan krijg je een melding.

Oudere werkmappen blijven werken. Een tijd in de naam zelf (Fien tot 13.00) of de kolom Wissel om wordt nog gelezen. De kolommen Van en Tot gaan voor.

Een casus kan een speciaal lokaal nodig hebben, zoals een keuken. Zet dat tussen haakjes achter het lokaal en de casus, bijvoorbeeld C1.36 (keuken) en K3 vrouw (keuken). Het programma zet de casus, samen met de beoordelaar, dan in een lokaal dat past. Lukt dat niet, dan krijg je een melding. De woorden tussen haakjes staan niet in het rooster.

Lokalen vullen: standaard krijgt op elk moment het lokaal met de minste studenten voorrang. Zo komt elke beoordelaar aan de beurt, ook als er minder simu's dan lokalen zijn. Krijgt een lokaal de hele dag niemand, dan staat bij Meldingen welk lokaal en waarom.

## Simu's

In het blad Simu staat per dag wie er is, eventueel met een begin- en eindtijd. Het programma gebruikt een simu alleen als die er de hele toets is.

Zodat simu's niet de hele dag dezelfde casus spelen, wisselen ze van lokaal. Bij de instellingen kies je wanneer: na elke pauze (standaard), na elke toets, of nooit.

Per simu kun je twee dingen instellen, in het blad Simu of met de knop Simucliënten in het programma:
- Vast lokaal: leeg betekent dat de simu meewisselt. Ja betekent dat de simu in één lokaal blijft. Je kunt ook een lokaalnaam invullen.
- Kan spelen: welke casussen de simu kan spelen, bijvoorbeeld vrouw, of P1, P2. Het woord moet als heel woord in de naam van de casus staan. Leeg betekent alles.

Je krijgt een melding bij te weinig simu's, bij een naam die twee keer voorkomt, bij een dag zonder simu's, of als niemand een casus kan spelen.

## Studenten

Het programma zoekt de kolommen op hun naam. De namen uit het bestaande bestand werken ook, zoals Roepnaam en Klas p2.

- Niet inroosteren bij: die beoordelaars krijgt de student niet. Meerdere namen scheid je met een komma, puntkomma of schuine streep.
- TTV: de student krijgt meer tijd en komt bij voorkeur vlak voor een pauze. Dan valt de extra tijd in de pauze.
- Voorkeur: Ochtend, Middag, Vroeg of Laat. Lukt een ochtend- of middagwens niet, dan krijg je een melding.
- Opmerkingen: woorden als ttv, ochtend en middag worden herkend. Elke opmerking staat bij Meldingen, zodat je kunt controleren of hij goed gelezen is. De hele tekst komt ook in het rooster.

Volgorde: eerst de studenten met TTV, dan die met een voorkeur, dan de rest. Een student zonder plek verdwijnt nooit. Hij staat onderaan het rooster als NIET INGEROOSTERD.

## Eerste kans en herkansing

De eerste kans roostert iedereen in die geen herkanser is. Daarna schrijft het programma in het blad Studenten op wanneer en bij wie elke student was.

De herkansing roostert alleen de herkansers in. Het programma probeert dan een andere beoordelaar en een andere casus te kiezen dan bij de eerste kans. Bij de instellingen kies je of dat een voorkeur is of verplicht.

## Toetsdag als lijst

In plaats van het blad Toetsdag kun je de dag ook als lijst opschrijven: in kolom A een kopje, in kolom B de waarden eronder.

| A | B |
|---|---|
| datum | 15-12-2026 |
| inzet | Ann |
| | Fien ochtend tot 13.00 |
| | Hans middag vanaf 13.30 |
| | Ida (reactie nog afwachten) |
| tijden | 10.00 - 10.15 |
| | 10.20 - 10.35 |
| pauzes | 11.15-11.40 |
| lokalen | A1 |
| casussen | K1 man |
| simu's | 7 x |

Zo wordt het gelezen:
- Lokalen en casussen horen in dezelfde volgorde bij elkaar.
- Iemand die de hele dag kan, krijgt een eigen lokaal.
- Mensen die alleen een deel van de dag kunnen, delen een lokaal, in volgorde van tijd.
- Iemand met een opmerking tussen haakjes is reserve. Een reserve wordt alleen ingezet als er te weinig beoordelaars zijn.
- De tijden en pauzes uit de lijst gaan voor de instellingen.
- Bij 7 x worden de eerste zeven simu's van die dag gebruikt.

Staat zo'n lijst in de werkmap, dan gaat die voor het blad Toetsdag. In het programma haal je een lijst uit een ander bestand binnen met Concept laden.

## Datums

Datums mogen op veel manieren, bijvoorbeeld 14-04-2026, 14-4-26, 2026-04-14 of 14 april 2026. Een datum zonder jaartal wordt niet geaccepteerd.

## Fouten en meldingen

Eerst wordt alles gecontroleerd. Bij een fout blijft het rooster ongewijzigd en staat bij Meldingen wat er mis is. Voorbeelden:
- een blad of kolom ontbreekt;
- een lokaal staat twee keer op dezelfde dag;
- een tijd klopt niet, of Van ligt na Tot;
- een datum heeft geen jaartal.

Meldingen die geen fout zijn, zoals een simu die twee keer voorkomt, staan er ook. Het rooster wordt dan wel gemaakt.

## Wat je terugkrijgt

- Het volledige rooster, met lege plekken als Vrije plek.
- Een uitdraai voor studenten, met alleen naam, lokaal en tijd.
- De meldingen.
- In het programma ook een pdf voor docenten (een pagina per lokaal) en een pdf voor studenten. Vrije plekken staan niet in de uitdraai en niet in de pdf's.

## Wat het nog niet kan

- De pauzes gelden voor alle dagen en alle lokalen.
- Een lijst (concept) zegt niet of het om de eerste kans of de herkansing gaat. Hij geldt voor wat je kiest.
- Woorden tussen haakjes (zoals keuken) en Kan spelen moeten hetzelfde gespeld zijn. Hoofdletters tellen niet mee.
- Het Word-overzicht van de opleiding wordt niet ingelezen.

## Alle instellingen

Deze staan in het blad Instellingen en op de pagina Instellingen in het programma. Ontbreekt een regel, dan vult het programma die aan met de standaardwaarde.

<!-- tabel: gegenereerd uit rooster_core.INSTELLINGEN -->
| Groep | Instelling | Standaard | Uitleg |
|---|---|---|---|
| Toetsdag | Eerste toets om | 09:40 | Begintijd van de eerste student. |
| Toetsdag | Laatste toets klaar om | 17:00 | Geen toets loopt later door dan deze tijd. |
| Toetsdag | Wisseltijd (min) | 5 | Tijd tussen twee studenten. |
| Toetsdag | Lokalen vullen | Evenredig | Evenredig: op elk tijdstip eerst het lokaal met de minste studenten, zodat elk lokaal (en elke beoordelaar) ongeveer evenveel krijgt, ook als er minder simu's dan lokalen zijn. Op volgorde: eerst de bovenste lokalen. Keuzes: Evenredig / Op volgorde. |
| Toetsduur | Jaar | 1 | Studiejaar van deze toets; bepaalt welke duur hieronder geldt. |
| Toetsduur | Toetsduur jaar 1 (min) | 15 | Gewone toets in jaar 1. |
| Toetsduur | TTV-toetsduur jaar 1 (min) | 20 | Toets met tijdverlenging in jaar 1. |
| Toetsduur | Toetsduur jaar 2 (min) | 15 | Gewone toets in jaar 2. |
| Toetsduur | TTV-toetsduur jaar 2 (min) | 20 | Toets met tijdverlenging in jaar 2. |
| Pauze | Pauzes | 11:15-11:40, 13:00-13:55, 15:15-15:40 | Van-tot, meerdere gescheiden door een komma. Leeg = geen pauze. |
| Pauze | Casus na pauze | Na pauze 1 | Wanneer slots de casus uit de kolom 'Casus na pauze' krijgen (alleen als die kolom is ingevuld). Keuzes: Nee / Na pauze 1 / Na pauze 2 / Na pauze 3 / Na elke pauze afwisselen. |
| TTV | TTV-plaatsing | Eind van blok vóór pauze | Waar TTV-studenten bij voorkeur komen. Aan het eind van een blok valt de extra tijd in de pauze. Keuzes: Eind van blok vóór pauze / Zo vroeg mogelijk. |
| TTV | TTV-studenten eerst inroosteren | Ja | Geeft TTV-studenten als eerste een plek, zodat de beste plekken voor hen vrij zijn. Keuzes: Ja / Nee. |
| Voorkeur | Middag begint om | 12:00 | Grens tussen voorkeur ochtend en middag. |
| Simucliënten | Simu's wisselen van lokaal | Na elke pauze | Na elke pauze of na elke toets schuift elke simucliënt een lokaal door, zodat niemand de hele dag bij dezelfde toets zit. Nee: iedere simu blijft in hetzelfde lokaal. Keuzes: Na elke pauze / Na elke toets / Nee. |
| Beoordelaars | Namen deels vergelijken | Ja | ‘Ann’ sluit dan ook ‘Anneke’ uit. Vangt spelfouten op, maar kan te veel uitsluiten. Keuzes: Ja / Nee. |
| Herkansing | Andere beoordelaar dan 1e kans | Voorkeur | Verplicht: lukt het niet, dan wordt de student niet ingeroosterd. Keuzes: Voorkeur / Verplicht / Maakt niet uit. |
| Herkansing | Andere casus dan 1e kans | Voorkeur | Verplicht: lukt het niet, dan wordt de student niet ingeroosterd. Keuzes: Voorkeur / Verplicht / Maakt niet uit. |
| Uitvoer | Vrije plekken tonen | Ja | Lege maar bruikbare plekken als 'Vrije plek' in het volledige rooster (nooit op de uitdraai of in de PDF's). Keuzes: Ja / Nee. |
| Uitvoer | Rooster sorteren op | Lokaal, dan tijd | Volgorde van het volledige rooster (altijd eerst per datum). Keuzes: Lokaal, dan tijd / Tijd, dan lokaal. |
| Uitvoer | Uitdraai sorteren op | Achternaam | Volgorde van de uitdraai voor studenten. Keuzes: Achternaam / Tijd / Lokaal, dan tijd. |
| Uitvoer | Datum op uitdraai | Ja | Nee: alleen de begintijd (handig als alles op één dag is). Keuzes: Ja / Nee. |
| Bladnamen | Blad studenten | Studenten | Naam van het blad. |
| Bladnamen | Blad toetsdag eerste kans | Toetsdag_Kans1 | Naam van het blad. |
| Bladnamen | Blad toetsdag herkansing | Toetsdag_Her | Naam van het blad. |
| Bladnamen | Blad simucliënten | Simu | Naam van het blad. |
| Bladnamen | Blad slots eerste kans (oud) | Slots_Kans1 | Naam van het blad. |
| Bladnamen | Blad slots herkansing (oud) | Slots_Her | Naam van het blad. |
| Bladnamen | Blad beoordelaars (oud) | Beoordelaars | Naam van het blad. |
| Bladnamen | Blad rooster eerste kans | Rooster_Kans1 | Naam van het blad. |
| Bladnamen | Blad rooster herkansing | Rooster_Her | Naam van het blad. |
| Bladnamen | Blad uitdraai eerste kans | Uitdraai_Kans1 | Naam van het blad. |
| Bladnamen | Blad uitdraai herkansing | Uitdraai_Her | Naam van het blad. |
| Bladnamen | Blad meldingen | Meldingen | Naam van het blad. |
