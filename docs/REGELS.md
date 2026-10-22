# Roosterregels (eerste kans en herkansing)

De Office Scripts en de desktop-app gebruiken exact dezelfde regels. De tests controleren dat beide dezelfde uitvoer geven.

## Werkwijze in het kort

Je vult drie dingen in. Het programma maakt de rest.

1. **Studenten**: één rij per student. Kolommen worden op kopnaam gevonden. Ook de namen uit het echte bestand werken (*Roepnaam*, *Klas p2*, *Niet inroosteren bij SB-docent P2*). Optioneel:
   - *TTV* (Ja);
   - *Voorkeur* (Ochtend / Middag / Vroeg / Laat);
   - *Opmerkingen*;
   - *IsHerkanser* (Ja).
2. **Toetsdag_Kans1** / **Toetsdag_Her**: één rij per lokaal per toetsdag, met deze kolommen:
   - *Datum*, *Lokaal*, *Casus*;
   - *Casus na pauze* (optioneel), *Vaardigheid*, *Beoordelaar*;
   - *Beoordelaar 2* en *Wissel om* (optioneel), voor een wissel halverwege de dag. Bijvoorbeeld: Huub tot 12:25, daarna Gerdien.
3. **Simu**: één rij per simucliënt per toetsdag: *Datum*, *simucliënt*, en optioneel *Vanaf*, *Tot*, *Vast lokaal* en *Kan spelen*. Een lege datum betekent elke dag. In de app vul je dit blad met **Simu's importeren…** vanuit het overzicht *Beschikbaarheid simu's*.

Uit de instellingen (eerste toets, laatste toets, toetsduur, wisseltijd en pauzes) maakt het programma alle slots. Met de standaardwaarden is dat elke 20 minuten een student (15 min toets + 5 min wissel): 09:40–11:15, 11:45–13:00, 14:00–15:15 en 15:45–17:00. Dat zijn 17 slots per lokaal, net als op de echte toetsdag van 14 april.

> **Standaard toetsduur gewijzigd:** van 10/15 naar **15 min, TTV 20 min**. De eerdere keuze kwam uit de oude testwerkmap, met slots per 10 minuten. Het echte rooster (M1.6 kans 1) gebruikt 15 minuten toets plus 5 minuten wissel. Pas het per toets aan bij Instellingen. De TTV-duur van 20 minuten is een aanname; controleer die.

**Of: conceptblad (lijstvorm).** Zo schrijf je het ook op papier op. In kolom A staan kopjes, in kolom B de waarden eronder (één per rij):

| A | B |
|---|---|
| datum | 15-12-2026 |
| inzet | Ann de Bruin |
| | … (één naam per rij) |
| | Fien ochtend tot 13.00 |
| | Hans middag vanaf 13.30 uur |
| | Ida Klaproos (reactie nog afwachten) |
| tijden | 10.00 - 10.15 |
| | 10.20 - 10.35 … |
| pauzes | 11.15-11.40 … |
| lokalen | A1 … |
| casussen | K1 man … (in dezelfde volgorde als de lokalen) |
| simu's | 7 x |
| studenten | (optioneel: één naam per rij, als er geen blad Studenten is) |

Zo wordt het gelezen:

- **Lokalen en casussen** worden op volgorde gekoppeld. Optioneel zijn er ook *vaardigheden* en *casussen na pauze*.
- **Inzet:**
  - Een gewone naam krijgt een lokaal voor de hele dag, in de volgorde van de lijst.
  - *ochtend/tot …* en *middag/vanaf …* vormen samen één lokaal, waarbij de tweede het na die tijd overneemt.
  - Een naam met een opmerking tussen haakjes is reserve. Een reserve wordt alleen ingezet als er anders te weinig beoordelaars zijn.
- **Tijden:** precies de tijden uit de lijst worden gebruikt. Dubbele tijden tellen één keer, met een melding. De toetsduur komt uit de tijden (10.00 - 10.15 = 15 min).
- **Tijden en pauzes** uit het concept gaan voor de instellingen.
- **"simu's: 7 x":** de eerste 7 simu's voor die datum uit het blad Simu worden gebruikt; de rest is reserve.

Staat er een conceptblad in de werkmap, dan gaat het voor het blad Toetsdag. Dat staat dan ook als melding bij Meldingen. In de app zet **Concept laden…** het concept uit een ander bestand in de open werkmap. Bij *Excel opslaan* wordt het bewaard als blad *Concept*.

**Oude werkwijze:** is het blad Toetsdag leeg en bestaat *Slots_Kans1* / *Slots_Her* (één rij per begintijd), dan worden de oude bladen gebruikt, samen met *Beoordelaars*. Een *Simu*-blad met een kolom *Tijd* wordt ook nog gelezen als één rij per slot.

## Beoordelaars die niet de hele dag kunnen, of ruilen

In het blad Toetsdag heeft elke beoordelaar eigen kolommen **Van** en **Tot**. Leeg betekent vanaf het begin of tot het eind van de dag. Voor meer beoordelaars in één lokaal voeg je *Beoordelaar 2* / *Van 2* / *Tot 2* toe, dan *Beoordelaar 3* / *Van 3* / *Tot 3*, enzovoort. Per toets neemt het lokaal de eerste beoordelaar die dan kan, en de toets moet binnen zijn of haar tijd passen.

| Lokaal | Beoordelaar | Van | Tot | Beoordelaar 2 | Van 2 | Tot 2 |
|---|---|---|---|---|---|---|
| C1.39 | Fien | | 13:00 | Hans | 13:30 | |
| A | Ann | | 13:00 | Bram | 13:00 | |
| B | Bram | | 13:00 | Ann | 13:00 | |
| C | Dorus | 10:00 | 12:00 | | | |

- In het voorbeeld ruilen **Ann en Bram** om 13:00 van lokaal. Staat iemand op dezelfde tijd in twee lokalen, dan volgt een waarschuwing.
- Een ongeldige tijd, of een *Van* na *Tot*, geeft een fout met het rijnummer.
- Dit werkt ook nog, maar de kolommen gaan voor:
  - een tijd in de cel zelf (`Fien tot 13.00`, `Hans vanaf 13.30`, `Dorus 10.00-12.00`);
  - **Wissel om**: beoordelaar 1 tot die tijd, beoordelaar 2 vanaf die tijd.
- In het **conceptblad** (lijstvorm) zet je de tijd achter de naam bij *inzet*. Wie maar een deel van de dag kan, komt op tijdvolgorde samen in één lokaal (bijv. `Eef 10.00-12.00` → `Dorus van 12.00 tot 15.20` → `Lot vanaf 15.20`).

**Lokalen vullen** (instelling):

- **Evenredig** (standaard): op elk tijdstip gaat het lokaal met de minste studenten voor. Zo doet elk lokaal en elke beoordelaar mee, ook als er minder simu's dan lokalen zijn.
- **Op volgorde:** eerst de bovenste lokalen.

Een lokaal dat de hele dag niemand kan krijgen, staat met naam, beoordelaars en reden bij Meldingen.

## Kenmerken: casus die een bepaald lokaal nodig heeft

Zet kenmerken tussen haakjes achter het lokaal en achter de casus. Dat kan in het blad Toetsdag en in het conceptblad:

- lokaal `C1.36 (keuken)`, `Praktijkhuis (keuken, tillift)`;
- casus `K3 vrouw (keuken)`.

Zo wordt het verwerkt:

- Een casus die een kenmerk vraagt, gaat met zijn beoordelaar en vaardigheid naar een lokaal dat die kenmerken heeft.
  - De casus met de minste mogelijke lokalen gaat eerst.
  - Staat de casus al in een passend lokaal, dan blijft hij daar.
- De andere casussen vullen de overige lokalen op volgorde.
- Elke verschuiving staat bij Meldingen. Is er geen passend lokaal vrij, dan volgt een waarschuwing.
- De kenmerken zelf staan niet in het rooster of de PDF's.
- Ook *Casus na pauze* kan een kenmerk vragen. Het lokaal ligt dan al vast, dus dat wordt alleen gecontroleerd.

## Kan spelen: welke simu welke casus speelt

Kolom *Kan spelen* in het blad Simu, of in de app via **Simucliënten…**:

- leeg betekent alle casussen;
- anders een of meer woorden of casusnamen, gescheiden door `,` `;` of `/`, bijvoorbeeld `vrouw` of `P1, P2`. Een woord moet als heel woord in de casusnaam staan: `vrouw` past op *P3 vrouw*, `P1` niet op *P10*.

Zo wordt het verwerkt:

- Simu's wisselen alleen naar lokalen met een casus die ze kunnen spelen.
- Een waarschuwing volgt als niemand van die dag een casus kan spelen.
- Een waarschuwing volgt ook als een vaste simu de casus van zijn lokaal niet kan spelen.

## Uitvoer

- **Rooster_Kans1 / Rooster_Her**: het volledige rooster voor de organisatie. Lege, bruikbare plekken staan erin als **Vrije plek**, met lokaal, casus, beoordelaar en simucliënt. Dat kun je uitzetten.
- **Uitdraai_Kans1 / Uitdraai_Her**: alleen naam, lokaal en tijd, om te publiceren. Hier staan nooit vrije plekken in.
- **Meldingen**: telling, waarschuwingen en fouten, plus elke opmerking uit *Opmerkingen*, met hoe die is gelezen. Controleer die opmerkingen altijd.
- **App: PDF voor docenten** (per lokaal per dag een pagina) en **PDF voor studenten**. In geen van beide staan vrije plekken.

## Feedback → hoe het nu werkt

| Feedback | Uitwerking |
|---|---|
| Casus vóór de pauze, een andere erna | Kolom **Casus na pauze** in het blad Toetsdag, plus de instelling *Casus na pauze*: na pauze 1, 2 of 3, of afwisselend na elke pauze. Een waarschuwing volgt als beide casussen gelijk zijn. |
| Uitdraai voor studenten zonder studentnummer, casus etc. | Bladen **Uitdraai_*** en de PDF voor studenten: alleen naam, lokaal en tijd. |
| TTV | *TTV* = Ja, of 'ttv' in *Opmerkingen*. De student krijgt de TTV-duur en komt bij voorkeur in het **laatste slot vóór een pauze**, zodat de extra tijd in de pauze valt. |
| Jaar 2 tijd anders | Instelling **Jaar** kiest welke toetsduur geldt. Per jaar is er een gewone duur en een TTV-duur. |
| 30 voor 45 min toets | Nog niet eenduidig. Alle duren zijn instelbaar; de standaard volgt het echte rooster (15 + 5 min). |
| Lokaal + casus | Het rooster staat per datum → lokaal → tijd. Per lokaal staan de casus en de vaardigheid erbij. |

## Instellingen

Alle instellingen staan in het blad **Instellingen** en in de app op de pagina *Instellingen*. Beide gebruiken dezelfde lijst (`INSTELLINGEN` in `app/rooster_core.py`); `tools/bouw_scripts.py` zet die lijst ook in de Office Scripts.

- Ontbreekt een rij, dan wordt die aangevuld met de standaardwaarde.
- Een ongeldige waarde geeft een fout op het blad Meldingen. Het rooster blijft dan ongewijzigd.

<!-- tabel: gegenereerd uit rooster_core.INSTELLINGEN -->
| Groep | Instelling | Standaard | Wat het doet |
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

## Planningsregels

1. **Slots.** Per rij in het blad Toetsdag komt er een slot op elke begintijd. Een gewone toets raakt nooit een pauze en loopt nooit na *Laatste toets klaar om*.
2. **Beoordelaar.** Per lokaal staat de beoordelaar uit het blad Toetsdag. Na *Wissel om* is dat *Beoordelaar 2*.
3. **Simucliënten** komen uit het blad Simu, voor die datum. Per slot wordt alleen gebruikt wie dan volgens *Vanaf*/*Tot* beschikbaar is.
   - Met *Simu's wisselen van lokaal* = **Na elke pauze** krijgt lokaal *k* simu *(k + aantal pauzes) mod n*.
   - Met **Na elke toets** krijgt lokaal *k* simu *(k + hoeveelste tijd van de dag) mod n*, zodat elke simu na iedere toets een lokaal doorschuift en niet de hele dag bij dezelfde toets zit.
   - Met **Nee** blijft iedere simu in hetzelfde lokaal.

   De beoordelaar en de casus blijven de hele dag in hun lokaal. Alleen de simu's schuiven door, zodat ze niet steeds dezelfde casus spelen.

   **Per simu** kan dat anders, via de kolom *Vast lokaal* in het blad Simu (of in de app met **Simucliënten…**):
   - leeg: wisselt mee volgens de instelling;
   - *Ja*: blijft de hele dag in één lokaal (het eerste lokaal dat nog vrij is);
   - een lokaalnaam, bijvoorbeeld *C1.39*: blijft altijd in dat lokaal.

   De andere simu's wisselen dan alleen tussen de overige lokalen. Een onbekend of al bezet lokaal geeft een waarschuwing; die simu wisselt dan gewoon mee.

   Er volgt een waarschuwing:
   - bij minder simu's dan lokalen;
   - bij een dubbele naam;
   - bij een dag zonder simu's.
4. **Uitsluitingen.** Beoordelaars in *Niet inroosteren bij …* worden voor die student overgeslagen. Namen scheid je met `,` `;` of `/` (bijvoorbeeld `Floor/Huub`). Met *Namen deels vergelijken* telt een deel van de naam ook.
5. **Volgorde:**
   - eerst TTV-studenten;
   - dan studenten met een voorkeur;
   - dan de rest, in de volgorde van het blad Studenten.

   Plaatsing:
   - TTV: het slot dat het dichtst vóór een pauze begint.
   - *Ochtend*: het vroegste slot vóór *Middag begint om*.
   - *Middag*: het vroegste slot daarna.
   - *Vroeg*: het vroegste slot.
   - *Laat*: het laatste slot.

   Een gemiste ochtend- of middagwens geeft een waarschuwing.
6. **TTV-toets.** Mag doorlopen in de pauze direct erna.
7. **Opmerkingen.** De woorden *ttv*, *ochtend*, *middag*, *vroeg* en *laat* worden herkend. Elke opmerking staat op Meldingen om te controleren, en de volledige tekst staat in *bijzheden*.
8. **Eerste kans** roostert iedereen met `IsHerkanser` ≠ `Ja` in. Daarna schrijft het `EersteDatum`, `EersteTijd`, `EersteBeoordelaar` en `EersteCasus` terug in het blad Studenten.
9. **Herkansing** roostert alleen `IsHerkanser` = `Ja` in. Een andere beoordelaar en een andere casus dan bij de eerste kans kun je instellen als *Voorkeur*, *Verplicht* of *Maakt niet uit*.
10. **Niemand verdwijnt.** Wie niet past, staat onderaan het rooster met `NIET INGEROOSTERD` en op Meldingen.
11. **Eerst controleren.** Bij een fout blijft het rooster ongewijzigd. Voorbeelden van fouten:
   - een ontbrekend blad of een ontbrekende kolom;
   - een dubbel lokaal;
   - *Beoordelaar 2* zonder *Wissel om*;
   - een ongeldige tijd of pauze.

## Bekende beperkingen

- De pauzes gelden voor alle dagen en alle lokalen.
- Een simucliënt rouleert per blok en alleen als hij het hele blok beschikbaar is (*Vanaf*/*Tot*).
- Simu's met '?' in het beschikbaarheidsoverzicht worden bij importeren niet vooraf aangevinkt.
- Het Word-bestand *Overzichtslijst* wordt niet ingelezen. Het is alleen naslag; de bevestigde simu's staan ook in het beschikbaarheidsoverzicht.
