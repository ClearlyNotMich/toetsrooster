# Roosterregels (eerste kans en herkansing)

De Office Scripts en de desktop-app gebruiken exact dezelfde regels.

## Feedback → hoe het nu werkt

| Feedback | Uitwerking |
|---|---|
| Casus vóór de pauze, een andere erna | Blad **Instellingen**: `Pauze van` / `Pauze tot`. In de slotbladen staat een optionele kolom **Casus na pauze**: slots na de pauze krijgen die casus. Slots ín de pauze worden overgeslagen. Wordt in een lokaal dezelfde casus vóór én na de pauze gebruikt, dan verschijnt er een waarschuwing. |
| Uitdraai voor studenten zonder studentnummer, casus etc. | Nieuwe bladen **Uitdraai_Kans1** / **Uitdraai_Her** met alleen *Naam*, *Lokaal* en *Tijd* (datum + begintijd), gesorteerd op achternaam. |
| TTV | Kolom **TTV** = `Ja` → de student krijgt de TTV-toetsduur en komt bij voorkeur in het **laatste slot vóór de pauze**, zodat de extra tijd in de pauze valt (zoals de notitie "einde van het blok voor pauze extra tijd"). Zonder pauze: laatste slot van de dag. Bijzonderheden toont `TTV (45 min)`. |
| Jaar 2 tijd anders | Instellingen **Jaar** (1 of 2) kiest welke toetsduur geldt; per jaar staan een gewone en een TTV-duur. *Standaard staan beide jaren op 30/45: vul de juiste tijd voor jaar 2 in.* |
| 30 voor 45 min toets | *Beste inschatting:* gewone toets 30 min, TTV-toets 45 min (instelbaar). |
| Lokaal + casus | Het volledige rooster is gesorteerd op datum → lokaal → tijd, zodat per lokaal de casus in één blok staat; kolommen Lokaal en Casus staan erin. |

## Planningsregels

1. Elke rij in `Slots_Kans1` / `Slots_Her` is een mogelijke **begintijd** in een lokaal. Slots mogen in stappen van 10 minuten staan: een toets van 30 minuten blokkeert het lokaal, de beoordelaar en de simucliënt tot de eindtijd, zodat overlappende slots vanzelf vervallen.
2. Een gewone toets moet vóór `Pauze van` klaar zijn. Een TTV-toets mag doorlopen tot `Pauze tot`.
3. Beoordelaar en simucliënt moeten op de **begintijd** in hun blad staan en mogen op dat moment geen andere student hebben. Staat er bij hen een *Casus* (of bij de simucliënt een *Lokaal*), dan worden ze alleen daarvoor ingezet.
4. Beoordelaars die in *Niet inroosteren bij SB-docent* of *Niet inroosteren bij de vaardighedendocent* staan, worden voor die student overgeslagen. Meerdere namen scheid je met `,` of `;`. Een deel van de naam is genoeg, net als in het oude script.
5. Volgorde van inroosteren:
   - Eerst de TTV-studenten, daarna de rest, in de volgorde van het blad Studenten.
   - Een gewone student krijgt het vroegste slot dat past.
6. **Eerste kans** roostert iedereen met `IsHerkanser` ≠ `Ja` in en schrijft `EersteDatum`, `EersteTijd`, `EersteBeoordelaar` en `EersteCasus` terug in het blad Studenten. Dit herstelt de oude fout die één kolom te vroeg schreef.
7. **Herkansing** roostert alleen `IsHerkanser` = `Ja` in, met `Slots_Her`. Het eerst geprobeerde rooster gebruikt een andere beoordelaar én een andere casus dan bij de eerste kans. Lukt dat niet, dan mag hetzelfde. Dat staat dan in *bijzheden* en op het blad Meldingen.
8. Een student die niet past, verdwijnt niet:
   - de student staat onderaan het rooster met `NIET INGEROOSTERD`;
   - het blad **Meldingen** bevat een waarschuwing.
9. Eerst wordt alles gecontroleerd. Bij een fout, zoals een ontbrekend blad, ontbrekende kolom, ongeldige tijd of ongeldige instelling, blijft het rooster ongewijzigd en staat de fout op **Meldingen**.
10. Kolommen worden op **kopnaam** gevonden, niet op positie. Een extra kolom zoals `TTV` verschuift dus niets meer.

## Bekende beperkingen

- De beschikbaarheid van beoordelaar en simucliënt wordt alleen op de begintijd gecontroleerd, niet voor elke tien minuten van de toets.
- Na het laatste slot van de dag wordt niet gecontroleerd of de toets nog binnen de beschikbare tijd valt. Zet dus alleen begintijden in de slotbladen die nog passen.
- De pauze geldt voor alle dagen en alle lokalen.
