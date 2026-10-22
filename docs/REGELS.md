# Roosterregels (eerste kans en herkansing)

De Office Scripts en de desktop-app gebruiken exact dezelfde regels.

## Feedback → hoe het nu werkt

| Feedback | Uitwerking |
|---|---|
| Casus vóór de pauze, een andere erna | Blad **Instellingen**: `Pauze van` / `Pauze tot`. In de slotbladen staat een optionele kolom **Casus na pauze**: slots na de pauze krijgen die casus. Slots ín de pauze worden overgeslagen. Wordt in een lokaal dezelfde casus vóór én na de pauze gebruikt, dan verschijnt er een waarschuwing. |
| Uitdraai voor studenten zonder studentnummer, casus etc. | Nieuwe bladen **Uitdraai_Kans1** / **Uitdraai_Her** met alleen *Naam*, *Lokaal* en *Tijd* (datum + begintijd), gesorteerd op achternaam. |
| TTV | Kolom **TTV** = `Ja` → de student krijgt de TTV-toetsduur en komt bij voorkeur in het **laatste slot vóór de pauze**, zodat de extra tijd in de pauze valt (zoals de notitie "einde van het blok voor pauze extra tijd"). Zonder pauze: laatste slot van de dag. Bijzonderheden toont `TTV (15 min)`. |
| Jaar 2 tijd anders | Instellingen **Jaar** (1 of 2) kiest welke toetsduur geldt; per jaar staan een gewone en een TTV-duur. *Standaard staan beide jaren op 10/15 min: vul de juiste tijd voor jaar 2 in.* |
| 30 voor 45 min toets | Niet eenduidig. De slots, beoordelaars en simucliënten in de werkmap staan per **10 minuten**, en het oude script gaf iedere rij één student. Daarom is besloten: **gewone toets 10 min (één slot), TTV 15 min** (instelbaar). Een eerdere inschatting van 30/45 min paste maar 8 van de 12 studenten in de echte werkmap. Bedoel je echt 30/45 min, vul dat dan in bij Instellingen. |
| Lokaal + casus | Het volledige rooster is gesorteerd op datum → lokaal → tijd, zodat per lokaal de casus in één blok staat; kolommen Lokaal en Casus staan erin. |

## Instellingen

Alle instellingen staan in het blad **Instellingen**, en in de app op de pagina *Instellingen*. Beide gebruiken dezelfde lijst (`INSTELLINGEN` in `app/rooster_core.py`). `tools/bouw_scripts.py` zet die lijst ook in de Office Scripts.

- Ontbreekt een rij, dan vult het script of de app die aan met de standaardwaarde.
- Een ongeldige waarde geeft een fout op het blad Meldingen. Het rooster blijft dan ongewijzigd.

<!-- tabel: gegenereerd uit rooster_core.INSTELLINGEN -->
| Groep | Instelling | Standaard | Wat het doet |
|---|---|---|---|
| Toetsduur | Jaar | 1 | Studiejaar van deze toets; bepaalt welke duur hieronder geldt. |
| Toetsduur | Toetsduur jaar 1 (min) | 10 | Gewone toets in jaar 1 (10 min = één slot). |
| Toetsduur | TTV-toetsduur jaar 1 (min) | 15 | Toets met tijdverlenging in jaar 1. |
| Toetsduur | Toetsduur jaar 2 (min) | 10 | Gewone toets in jaar 2. |
| Toetsduur | TTV-toetsduur jaar 2 (min) | 15 | Toets met tijdverlenging in jaar 2. |
| Pauze | Pauze van | (leeg) | Begin van de pauze, bijv. 12:00. |
| Pauze | Pauze tot | (leeg) | Einde van de pauze, bijv. 12:30. |
| Pauze | Casus na pauze gebruiken | Ja | Slots na de pauze krijgen de casus uit de kolom 'Casus na pauze'. Keuzes: Ja / Nee. |
| TTV | TTV-plaatsing | Eind van blok vóór pauze | Waar TTV-studenten bij voorkeur komen. Aan het eind van het blok valt de extra tijd in de pauze. Keuzes: Eind van blok vóór pauze / Zo vroeg mogelijk. |
| TTV | TTV-studenten eerst inroosteren | Ja | Geeft TTV-studenten als eerste een plek, zodat de beste plekken voor hen vrij zijn. Keuzes: Ja / Nee. |
| Beoordelaars | Namen deels vergelijken | Ja | ‘Ann’ sluit dan ook ‘Anneke’ uit. Vangt spelfouten op, maar kan te veel uitsluiten. Keuzes: Ja / Nee. |
| Herkansing | Andere beoordelaar dan 1e kans | Voorkeur | Verplicht: lukt het niet, dan wordt de student niet ingeroosterd. Keuzes: Voorkeur / Verplicht / Maakt niet uit. |
| Herkansing | Andere casus dan 1e kans | Voorkeur | Verplicht: lukt het niet, dan wordt de student niet ingeroosterd. Keuzes: Voorkeur / Verplicht / Maakt niet uit. |
| Uitvoer | Rooster sorteren op | Lokaal, dan tijd | Volgorde van het volledige rooster (altijd eerst per datum). Keuzes: Lokaal, dan tijd / Tijd, dan lokaal. |
| Uitvoer | Uitdraai sorteren op | Achternaam | Volgorde van de uitdraai voor studenten. Keuzes: Achternaam / Tijd / Lokaal, dan tijd. |
| Uitvoer | Datum op uitdraai | Ja | Nee: alleen de begintijd (handig als alles op één dag is). Keuzes: Ja / Nee. |
| Bladnamen | Blad studenten | Studenten | Naam van het blad. |
| Bladnamen | Blad slots eerste kans | Slots_Kans1 | Naam van het blad. |
| Bladnamen | Blad slots herkansing | Slots_Her | Naam van het blad. |
| Bladnamen | Blad beoordelaars | Beoordelaars | Naam van het blad. |
| Bladnamen | Blad simucliënten | Simu | Naam van het blad. |
| Bladnamen | Blad rooster eerste kans | Rooster_Kans1 | Naam van het blad. |
| Bladnamen | Blad rooster herkansing | Rooster_Her | Naam van het blad. |
| Bladnamen | Blad uitdraai eerste kans | Uitdraai_Kans1 | Naam van het blad. |
| Bladnamen | Blad uitdraai herkansing | Uitdraai_Her | Naam van het blad. |
| Bladnamen | Blad meldingen | Meldingen | Naam van het blad. |

## Planningsregels

1. Elke rij in `Slots_Kans1` / `Slots_Her` is een mogelijke **begintijd** in een lokaal. Slots mogen in stappen van 10 minuten staan: een toets die langer is dan één slot (bijv. TTV 15 min) blokkeert het lokaal, de beoordelaar en de simucliënt tot de eindtijd, zodat overlappende slots vanzelf vervallen.
2. Een gewone toets moet vóór `Pauze van` klaar zijn. Een TTV-toets mag doorlopen tot `Pauze tot`.
3. Beoordelaar en simucliënt moeten op de **begintijd** in hun blad staan en mogen op dat moment geen andere student hebben. Staat er bij hen een *Casus* (of bij de simucliënt een *Lokaal*), dan worden ze alleen daarvoor ingezet.
4. Beoordelaars die in *Niet inroosteren bij SB-docent* of *Niet inroosteren bij de vaardighedendocent* staan, worden voor die student overgeslagen. Meerdere namen scheid je met `,` of `;`. Een deel van de naam is genoeg, net als in het oude script.
5. Volgorde van inroosteren:
   - Eerst de TTV-studenten, daarna de rest, in de volgorde van het blad Studenten.
   - Een gewone student krijgt het vroegste slot dat past.
6. **Eerste kans** roostert iedereen met `IsHerkanser` ≠ `Ja` in en schrijft `EersteDatum`, `EersteTijd`, `EersteBeoordelaar` en `EersteCasus` terug in het blad Studenten. Dit herstelt de oude fout die één kolom te vroeg schreef.
7. **Herkansing** roostert alleen `IsHerkanser` = `Ja` in, met `Slots_Her`. Of de beoordelaar en de casus anders moeten zijn dan bij de eerste kans, stel je in:
   - *Voorkeur*: eerst anders proberen; lukt dat niet, dan mag hetzelfde. Dat staat dan in *bijzheden* en op Meldingen.
   - *Verplicht*: het moet anders.
   - *Maakt niet uit*: geen eis.
8. Een student die niet past, verdwijnt niet:
   - de student staat onderaan het rooster met `NIET INGEROOSTERD`;
   - het blad **Meldingen** bevat een waarschuwing.
9. Eerst wordt alles gecontroleerd. Bij een fout, zoals een ontbrekend blad, ontbrekende kolom, ongeldige tijd of ongeldige instelling, blijft het rooster ongewijzigd en staat de fout op **Meldingen**.
10. Kolommen worden op **kopnaam** gevonden, niet op positie. Een extra kolom zoals `TTV` verschuift dus niets meer.

## Bekende beperkingen

- De beschikbaarheid van beoordelaar en simucliënt wordt alleen op de begintijd gecontroleerd, niet voor elke tien minuten van de toets.
- Na het laatste slot van de dag wordt niet gecontroleerd of de toets nog binnen de beschikbare tijd valt. Zet dus alleen begintijden in de slotbladen die nog passen.
- De pauze geldt voor alle dagen en alle lokalen.
