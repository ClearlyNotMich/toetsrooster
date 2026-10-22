"""Roosterlogica voor OWB-toetsen (eerste kans en herkansing).

Dit is dezelfde logica als in de Office Scripts (`OWB * Roster Generator.txt`).
Wijzig je hier iets, wijzig het daar ook; tests/test_parity.py controleert dat
beide exact dezelfde uitvoer geven.

Invoer en uitvoer zijn "matrices": lijsten van rijen zoals Excel `getValues()`
ze geeft (datums als serienummers, tijden als dagfracties, lege cellen als "").
"""
from __future__ import annotations

import datetime as dt
import math
import re

KANS1 = "kans1"
HER = "her"
# Bladnamen komen uit de instellingen (sleutels hieronder).
MODI = {
    KANS1: {"naam": "Eerste kans", "slots": "blad_slots1", "rooster": "blad_rooster1", "uitdraai": "blad_uitdraai1"},
    HER: {"naam": "Herkansing", "slots": "blad_slots_her", "rooster": "blad_rooster_her", "uitdraai": "blad_uitdraai_her"},
}
INSTELLINGEN_BLAD = "Instellingen"
INSTELLINGEN_KOP = ["Instelling", "Waarde", "Toelichting"]
ROOSTER_KOP = ["Datum", "Tijd", "Lokaal", "Casus", "Vaardigheid", "Beoordelaar", "simucliënt", "stnr",
               "Voornaam", "vv", "Achternaam", "klas", "bijzheden", "Eindtijd"]
UITDRAAI_KOP = ["Naam", "Lokaal", "Tijd"]
MELDINGEN_KOP = ["Soort", "Melding"]
EERSTE_KOP = ["EersteDatum", "EersteTijd", "EersteBeoordelaar", "EersteCasus"]
JA_NEE = ["Ja", "Nee"]
VOORKEUR = ["Voorkeur", "Verplicht", "Maakt niet uit"]
GROEPEN = {
    "Toetsduur": "Hoe lang een toets het lokaal, de beoordelaar en de simucliënt bezet houdt.",
    "Pauze": "Tijdens de pauze wordt niemand ingeroosterd. Laat beide tijden leeg voor een dag zonder pauze.",
    "TTV": "Studenten met toegestane tijdverlenging (kolom TTV = Ja).",
    "Beoordelaars": "Uitsluitingen uit de kolommen 'Niet inroosteren bij …' in het blad Studenten.",
    "Herkansing": "Wat er gebeurt als een herkanser opnieuw wordt ingeroosterd.",
    "Uitvoer": "Volgorde en inhoud van het rooster en de uitdraai voor studenten.",
    "Bladnamen": "Namen van de bladen in de werkmap. Alleen aanpassen als je bladen hebt hernoemd.",
}


def _inst(sleutel, groep, label, soort, standaard, uitleg, opties=(), min_=0, max_=0):
    return {"sleutel": sleutel, "groep": groep, "label": label, "soort": soort, "standaard": standaard,
            "uitleg": uitleg, "opties": list(opties), "min": min_, "max": max_}


# Eén bron voor de app, het blad Instellingen en de Office Scripts (tools/bouw_scripts.py zet deze lijst in de scripts).
INSTELLINGEN = [
    _inst("jaar", "Toetsduur", "Jaar", "getal", 1, "Studiejaar van deze toets; bepaalt welke duur hieronder geldt.", min_=1, max_=2),
    _inst("duur1", "Toetsduur", "Toetsduur jaar 1 (min)", "getal", 10, "Gewone toets in jaar 1 (10 min = één slot).", min_=1, max_=480),
    _inst("ttv1", "Toetsduur", "TTV-toetsduur jaar 1 (min)", "getal", 15, "Toets met tijdverlenging in jaar 1.", min_=1, max_=480),
    _inst("duur2", "Toetsduur", "Toetsduur jaar 2 (min)", "getal", 10, "Gewone toets in jaar 2.", min_=1, max_=480),
    _inst("ttv2", "Toetsduur", "TTV-toetsduur jaar 2 (min)", "getal", 15, "Toets met tijdverlenging in jaar 2.", min_=1, max_=480),
    _inst("pauze_van", "Pauze", "Pauze van", "tijd", "", "Begin van de pauze, bijv. 12:00."),
    _inst("pauze_tot", "Pauze", "Pauze tot", "tijd", "", "Einde van de pauze, bijv. 12:30."),
    _inst("casus_na", "Pauze", "Casus na pauze gebruiken", "keuze", "Ja",
          "Slots na de pauze krijgen de casus uit de kolom 'Casus na pauze'.", JA_NEE),
    _inst("ttv_plek", "TTV", "TTV-plaatsing", "keuze", "Eind van blok vóór pauze",
          "Waar TTV-studenten bij voorkeur komen. Aan het eind van het blok valt de extra tijd in de pauze.",
          ["Eind van blok vóór pauze", "Zo vroeg mogelijk"]),
    _inst("ttv_eerst", "TTV", "TTV-studenten eerst inroosteren", "keuze", "Ja",
          "Geeft TTV-studenten als eerste een plek, zodat de beste plekken voor hen vrij zijn.", JA_NEE),
    _inst("deelnaam", "Beoordelaars", "Namen deels vergelijken", "keuze", "Ja",
          "‘Ann’ sluit dan ook ‘Anneke’ uit. Vangt spelfouten op, maar kan te veel uitsluiten.", JA_NEE),
    _inst("her_beo", "Herkansing", "Andere beoordelaar dan 1e kans", "keuze", "Voorkeur",
          "Verplicht: lukt het niet, dan wordt de student niet ingeroosterd.", VOORKEUR),
    _inst("her_casus", "Herkansing", "Andere casus dan 1e kans", "keuze", "Voorkeur",
          "Verplicht: lukt het niet, dan wordt de student niet ingeroosterd.", VOORKEUR),
    _inst("rooster_sort", "Uitvoer", "Rooster sorteren op", "keuze", "Lokaal, dan tijd",
          "Volgorde van het volledige rooster (altijd eerst per datum).", ["Lokaal, dan tijd", "Tijd, dan lokaal"]),
    _inst("uitdraai_sort", "Uitvoer", "Uitdraai sorteren op", "keuze", "Achternaam",
          "Volgorde van de uitdraai voor studenten.", ["Achternaam", "Tijd", "Lokaal, dan tijd"]),
    _inst("uitdraai_datum", "Uitvoer", "Datum op uitdraai", "keuze", "Ja",
          "Nee: alleen de begintijd (handig als alles op één dag is).", JA_NEE),
    _inst("blad_studenten", "Bladnamen", "Blad studenten", "tekst", "Studenten", ""),
    _inst("blad_slots1", "Bladnamen", "Blad slots eerste kans", "tekst", "Slots_Kans1", ""),
    _inst("blad_slots_her", "Bladnamen", "Blad slots herkansing", "tekst", "Slots_Her", ""),
    _inst("blad_beo", "Bladnamen", "Blad beoordelaars", "tekst", "Beoordelaars", ""),
    _inst("blad_simu", "Bladnamen", "Blad simucliënten", "tekst", "Simu", ""),
    _inst("blad_rooster1", "Bladnamen", "Blad rooster eerste kans", "tekst", "Rooster_Kans1", ""),
    _inst("blad_rooster_her", "Bladnamen", "Blad rooster herkansing", "tekst", "Rooster_Her", ""),
    _inst("blad_uitdraai1", "Bladnamen", "Blad uitdraai eerste kans", "tekst", "Uitdraai_Kans1", ""),
    _inst("blad_uitdraai_her", "Bladnamen", "Blad uitdraai herkansing", "tekst", "Uitdraai_Her", ""),
    _inst("blad_meldingen", "Bladnamen", "Blad meldingen", "tekst", "Meldingen", ""),
]
STANDAARD = {i["sleutel"]: i["standaard"] for i in INSTELLINGEN}


# ---------------------------------------------------------------- hulpjes

def norm(v) -> str:
    return re.sub(r"[^a-z0-9]", "", tekst(v).lower())


def tekst(v) -> str:
    if v is None or v == "":
        return ""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    return str(v).strip()


def waar(v) -> bool:
    if v is True or (not isinstance(v, bool) and isinstance(v, (int, float)) and v == 1):
        return True
    t = tekst(v).lower()
    return t.startswith("ja") or t in ("x", "waar", "true")


def serie(j: int, m: int, d: int) -> int | None:
    try:
        return (dt.date(j, m, d) - dt.date(1899, 12, 30)).days
    except ValueError:
        return None


def naar_datum(v) -> int | None:
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return math.floor(v) if v >= 1 else None
    t = tekst(v)
    m = re.fullmatch(r"(\d{4})-(\d{1,2})-(\d{1,2})", t)
    if m:
        return serie(int(m[1]), int(m[2]), int(m[3]))
    m = re.fullmatch(r"(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})", t)
    if m:
        return serie(int(m[3]), int(m[2]), int(m[1]))
    return None


def naar_minuten(v) -> int | None:
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return math.floor((v - math.floor(v)) * 1440 + 0.5)
    m = re.fullmatch(r"(\d{1,2})[:.](\d{2})", tekst(v))
    if m and int(m[1]) < 24 and int(m[2]) < 60:
        return int(m[1]) * 60 + int(m[2])
    return None


def datum_tekst(d: int) -> str:
    x = dt.date(1899, 12, 30) + dt.timedelta(days=d)
    return f"{x.day:02d}-{x.month:02d}-{x.year}"


def tijd_tekst(minuten: int) -> str:
    return f"{minuten // 60:02d}:{minuten % 60:02d}"


def kolom(kop: list, *namen: str) -> int:
    genormd = [norm(k) for k in kop]
    for n in namen:
        if n in genormd:
            return genormd.index(n)
    return -1


def cel(rij: list, i: int):
    return rij[i] if 0 <= i < len(rij) else ""


def namen_lijst(v) -> list[str]:
    return [x.strip() for x in re.split(r"[,;]", tekst(v)) if x.strip()]


def beperkt(naam: str, verboden: list[str], deels: bool) -> bool:
    n = naam.strip().lower()
    return any(n == v.lower() or (deels and (v.lower() in n or n in v.lower())) for v in verboden)


def leeg(rij: list) -> bool:
    return all(tekst(x) == "" for x in rij)


# ---------------------------------------------------------------- inlezen

def toelichting(i: dict) -> str:
    return i["uitleg"] + (f" Keuzes: {' / '.join(i['opties'])}." if i["opties"] else "")


def instellingen_waarden(matrix: list | None) -> dict:
    """Sleutel -> ruwe waarde uit blad Instellingen (standaardwaarde als de rij ontbreekt)."""
    waarden = dict(STANDAARD)
    labels = {norm(i["label"]): i["sleutel"] for i in INSTELLINGEN}
    for rij in (matrix or [])[1:]:
        if norm(cel(rij, 0)) in labels:
            waarden[labels[norm(cel(rij, 0))]] = cel(rij, 1)
    return waarden


def instellingen_matrix(waarden: dict | None = None) -> list:
    """Blad Instellingen met standaardwaarden of de gegeven sleutel -> waarde."""
    return [INSTELLINGEN_KOP] + [[i["label"], (waarden or {}).get(i["sleutel"], i["standaard"]), toelichting(i)]
                                 for i in INSTELLINGEN]


def instellingen_aangevuld(matrix: list | None) -> list | None:
    """Blad Instellingen met ontbrekende rijen toegevoegd, of None als er niets ontbreekt."""
    if not matrix:
        return instellingen_matrix()
    aanwezig = {norm(cel(rij, 0)) for rij in matrix[1:]}
    nieuw = [[i["label"], i["standaard"], toelichting(i)] for i in INSTELLINGEN if norm(i["label"]) not in aanwezig]
    return [list(r) for r in matrix] + nieuw if nieuw else None


def lees_instellingen(matrix: list | None, fouten: list) -> dict:
    w = instellingen_waarden(matrix)
    s = {}
    for i in INSTELLINGEN:
        k, v, label = i["sleutel"], w[i["sleutel"]], i["label"]
        if i["soort"] == "getal":
            s[k] = int(tekst(v)) if tekst(v).isdigit() else -1
            if not i["min"] <= s[k] <= i["max"]:
                fouten.append(f"Instellingen: '{label}' moet een geheel getal van {i['min']} t/m {i['max']} zijn.")
                s[k] = i["standaard"]
        elif i["soort"] == "tijd":
            s[k] = naar_minuten(v) if tekst(v) else None
            if tekst(v) and s[k] is None:
                fouten.append(f"Instellingen: '{label}' moet een tijd zijn (bijv. 12:30) of leeg.")
        elif i["soort"] == "keuze":
            gevonden = [o for o in i["opties"] if norm(o) == norm(v)]
            s[k] = gevonden[0] if gevonden else i["standaard"]
            if not gevonden:
                fouten.append(f"Instellingen: '{label}' moet een van deze waarden zijn: {' / '.join(i['opties'])}.")
        else:
            s[k] = tekst(v) or i["standaard"]
            if not tekst(v):
                fouten.append(f"Instellingen: '{label}' mag niet leeg zijn.")
    s["duur"], s["ttv"] = s[f"duur{s['jaar']}"], s[f"ttv{s['jaar']}"]
    if (s["pauze_van"] is None) != (s["pauze_tot"] is None) or (
            s["pauze_van"] is not None and s["pauze_van"] >= s["pauze_tot"]):
        fouten.append("Instellingen: vul 'Pauze van' en 'Pauze tot' allebei in (van vóór tot), of laat beide leeg.")
        s["pauze_van"] = s["pauze_tot"] = None
    return s


def lees_studenten(matrix: list | None, blad: str, fouten: list, meldingen: list) -> tuple[list, list]:
    if not matrix:
        fouten.append(f"Blad '{blad}' ontbreekt of is leeg.")
        return [], []
    kop = list(matrix[0])
    k = {
        "nr": kolom(kop, "studentnummer", "stnr"), "voornaam": kolom(kop, "voornaam"),
        "tv": kolom(kop, "tussenvoegsel", "vv"), "achternaam": kolom(kop, "achternaam"), "klas": kolom(kop, "klas"),
        "niet_sb": kolom(kop, "nietinroosterenbijsbdocent"),
        "niet_vd": kolom(kop, "nietinroosterenbijdevaardighedendocent", "nietinroosterenbijvaardighedendocent"),
        "ttv": kolom(kop, "ttv"), "her": kolom(kop, "isherkanser", "herkanser"),
        "eb": kolom(kop, "eerstebeoordelaar"), "ec": kolom(kop, "eerstecasus"),
    }
    for naam in ("voornaam", "achternaam"):
        if k[naam] < 0:
            fouten.append(f"Blad '{blad}': kolom '{naam.capitalize()}' ontbreekt.")
    if fouten:
        return [], kop
    lijst = []
    oud = []
    for i, rij in enumerate(matrix[1:], start=1):
        if tekst(cel(rij, k["voornaam"])) == "" and tekst(cel(rij, k["achternaam"])) == "":
            continue
        her = cel(rij, k["her"])
        if isinstance(her, (int, float)) and not isinstance(her, bool) and her > 1:
            oud.append(str(i + 1))
        lijst.append({
            "i": i, "nr": tekst(cel(rij, k["nr"])), "voornaam": tekst(cel(rij, k["voornaam"])),
            "tv": tekst(cel(rij, k["tv"])), "achternaam": tekst(cel(rij, k["achternaam"])),
            "klas": tekst(cel(rij, k["klas"])),
            "verboden": namen_lijst(cel(rij, k["niet_sb"])) + namen_lijst(cel(rij, k["niet_vd"])),
            "ttv": waar(cel(rij, k["ttv"])), "her": waar(her),
            "eb": tekst(cel(rij, k["eb"])), "ec": tekst(cel(rij, k["ec"])),
        })
    if oud:
        meldingen.append(("Waarschuwing", f"{blad} rij {', '.join(oud)}: 'IsHerkanser' bevat een getal/datum "
                          "(restant van de oude scriptfout) en wordt gelezen als 'Nee'. Maak deze cellen leeg."))
    return lijst, kop


def lees_slots(matrix: list | None, blad: str, fouten: list) -> list:
    if not matrix:
        fouten.append(f"Blad '{blad}' ontbreekt of is leeg.")
        return []
    kop = list(matrix[0])
    kd, kt, kl = kolom(kop, "datum"), kolom(kop, "tijd"), kolom(kop, "lokaal")
    kc, kv, kn = kolom(kop, "casus"), kolom(kop, "vaardigheid"), kolom(kop, "casusnapauze")
    if min(kd, kt, kl) < 0:
        fouten.append(f"Blad '{blad}': kolommen 'Datum', 'Tijd' en 'Lokaal' zijn verplicht.")
        return []
    slots = []
    for i, rij in enumerate(matrix[1:], start=1):
        if leeg(rij):
            continue
        d, t = naar_datum(cel(rij, kd)), naar_minuten(cel(rij, kt))
        if d is None or t is None or tekst(cel(rij, kl)) == "":
            fouten.append(f"Blad '{blad}' rij {i + 1}: ongeldige of lege datum, tijd of lokaal.")
            continue
        slots.append({"n": len(slots), "d": d, "t": t, "lokaal": tekst(cel(rij, kl)), "casus": tekst(cel(rij, kc)),
                      "casus_na": tekst(cel(rij, kn)), "vaardigheid": tekst(cel(rij, kv))})
    return slots


def lees_beschikbaar(matrix: list | None, blad: str, namen: tuple, fouten: list) -> dict:
    if not matrix:
        fouten.append(f"Blad '{blad}' ontbreekt of is leeg.")
        return {}
    kop = list(matrix[0])
    kd, kt, kn = kolom(kop, "datum"), kolom(kop, "tijd"), kolom(kop, *namen)
    kc, kl = kolom(kop, "casus"), kolom(kop, "lokaal")
    if min(kd, kt, kn) < 0:
        fouten.append(f"Blad '{blad}': kolommen 'Datum', 'Tijd' en de naamkolom zijn verplicht.")
        return {}
    beschikbaar: dict = {}
    for i, rij in enumerate(matrix[1:], start=1):
        naam = tekst(cel(rij, kn))
        if naam == "":
            continue
        d, t = naar_datum(cel(rij, kd)), naar_minuten(cel(rij, kt))
        if d is None or t is None:
            fouten.append(f"Blad '{blad}' rij {i + 1}: ongeldige datum of tijd.")
            continue
        beschikbaar.setdefault(f"{d}_{t}", []).append(
            {"naam": naam, "casus": tekst(cel(rij, kc)), "lokaal": tekst(cel(rij, kl))})
    return beschikbaar


# ---------------------------------------------------------------- plannen

def maak_rooster(bladen: dict, modus: str) -> dict:
    """Berekent het rooster. Geeft {'fouten', 'meldingen', 'bladen', 'namen'} terug.

    'bladen' bevat de nieuwe inhoud van het rooster, de uitdraai, de meldingen en
    (alleen bij eerste kans) het studentenblad; bij fouten alleen de meldingen.
    Ontbreken er rijen in het blad Instellingen, dan wordt het aangevuld.
    """
    fouten: list[str] = []
    meldingen: list[tuple[str, str]] = []
    s = lees_instellingen(bladen.get(INSTELLINGEN_BLAD), fouten)
    m = MODI[modus]
    namen = {"rooster": s[m["rooster"]], "uitdraai": s[m["uitdraai"]], "meldingen": s["blad_meldingen"]}
    uit = {}
    aangevuld = instellingen_aangevuld(bladen.get(INSTELLINGEN_BLAD))
    if aangevuld:
        uit[INSTELLINGEN_BLAD] = aangevuld
    studenten, studenten_kop = lees_studenten(bladen.get(s["blad_studenten"]), s["blad_studenten"], fouten, meldingen)
    slots = lees_slots(bladen.get(s[m["slots"]]), s[m["slots"]], fouten)
    beoordelaars = lees_beschikbaar(bladen.get(s["blad_beo"]), s["blad_beo"], ("beoordelaar", "naam"), fouten)
    simus = lees_beschikbaar(bladen.get(s["blad_simu"]), s["blad_simu"], ("simuclint", "simu", "simulant", "naam"), fouten)
    if fouten:
        rijen = [MELDINGEN_KOP] + [["Fout", f] for f in fouten] + [list(x) for x in meldingen]
        rijen.append(["Info", f"{m['naam']}: rooster NIET aangepast door bovenstaande fouten."])
        uit[namen["meldingen"]] = rijen
        return {"fouten": fouten, "meldingen": meldingen, "bladen": uit, "namen": namen}

    pv, pt = s["pauze_van"], s["pauze_tot"]
    na_pauze = lambda t: pv is not None and t >= pt  # noqa: E731
    bruikbaar = []
    in_pauze = 0
    for slot in slots:
        if pv is not None and pv <= slot["t"] < pt:
            in_pauze += 1
            continue
        if na_pauze(slot["t"]) and slot["casus_na"] and s["casus_na"] == "Ja":
            slot["casus"] = slot["casus_na"]
        bruikbaar.append(slot)
    if in_pauze:
        meldingen.append(("Info", f"{in_pauze} slot(s) vallen in de pauze en zijn overgeslagen."))
    if pv is not None:
        gezien: dict = {}
        for slot in bruikbaar:
            if slot["casus"]:
                gezien.setdefault((slot["d"], slot["lokaal"]), [set(), set()])[1 if na_pauze(slot["t"]) else 0].add(slot["casus"])
        for (d, lokaal), (voor, na) in gezien.items():
            for c in sorted(voor & na):
                meldingen.append(("Waarschuwing", f"Lokaal {lokaal} op {datum_tekst(d)}: casus {c} wordt vóór én na de pauze gebruikt."))

    doel = [st for st in studenten if st["her"] == (modus == HER)]
    volgorde = [st for st in doel if st["ttv"]] + [st for st in doel if not st["ttv"]] if s["ttv_eerst"] == "Ja" else doel
    gewoon = sorted(bruikbaar, key=lambda x: (x["d"], x["t"], x["n"]))
    # Eind van blok vóór pauze: laatste slot eerst, zodat de extra tijd in de pauze valt.
    ttv_volgorde = sorted(bruikbaar, key=lambda x: (x["d"], 1 if na_pauze(x["t"]) else 0, -x["t"], x["n"])) \
        if s["ttv_plek"] == "Eind van blok vóór pauze" else gewoon
    deels = s["deelnaam"] == "Ja"
    bezet: dict = {}

    def vrij(sleutel, a, b):
        return all(b <= x or a >= y for x, y in bezet.get(sleutel, []))

    def anders(regel, strikt):
        # Moet het anders dan bij de 1e kans? Verplicht altijd, Voorkeur alleen in de eerste (strikte) ronde.
        return modus == HER and (s[regel] == "Verplicht" or (strikt and s[regel] == "Voorkeur"))

    def kies(lijst, slot, a, b, soort, st, strikt):
        for kandidaat in lijst:
            if kandidaat["casus"] and norm(kandidaat["casus"]) != norm(slot["casus"]):
                continue
            if kandidaat["lokaal"] and norm(kandidaat["lokaal"]) != norm(slot["lokaal"]):
                continue
            if soort == "b" and beperkt(kandidaat["naam"], st["verboden"], deels):
                continue
            if soort == "b" and anders("her_beo", strikt) and st["eb"] and norm(kandidaat["naam"]) == norm(st["eb"]):
                continue
            if vrij((soort, slot["d"], kandidaat["naam"]), a, b):
                return kandidaat["naam"]
        return None

    def probeer(st, strikt):
        duur = s["ttv"] if st["ttv"] else s["duur"]
        for slot in (ttv_volgorde if st["ttv"] else gewoon):
            a, b = slot["t"], slot["t"] + duur
            if pv is not None and a < pv and b > (pt if st["ttv"] else pv):
                continue
            if anders("her_casus", strikt) and st["ec"] and norm(slot["casus"]) == norm(st["ec"]):
                continue
            if not vrij(("l", slot["d"], slot["lokaal"]), a, b):
                continue
            sleutel = f"{slot['d']}_{slot['t']}"
            beo = kies(beoordelaars.get(sleutel, []), slot, a, b, "b", st, strikt)
            simu = beo and kies(simus.get(sleutel, []), slot, a, b, "s", st, strikt)
            if not simu:
                continue
            for k in (("l", slot["d"], slot["lokaal"]), ("b", slot["d"], beo), ("s", slot["d"], simu)):
                bezet.setdefault(k, []).append((a, b))
            return {"st": st, "slot": slot, "eind": b, "beo": beo, "simu": simu}
        return None

    toegewezen: dict = {}
    for strikt in ([True, False] if modus == HER else [False]):
        for st in volgorde:
            if st["i"] not in toegewezen:
                r = probeer(st, strikt)
                if r:
                    toegewezen[st["i"]] = r

    if s["rooster_sort"] == "Lokaal, dan tijd":
        rooster_sleutel = lambda r: (r["slot"]["d"], r["slot"]["lokaal"].lower(), r["slot"]["t"], r["slot"]["n"])  # noqa: E731
    else:
        rooster_sleutel = lambda r: (r["slot"]["d"], r["slot"]["t"], r["slot"]["lokaal"].lower(), r["slot"]["n"])  # noqa: E731
    if s["uitdraai_sort"] == "Achternaam":
        uitdraai_sleutel = lambda r: (r["st"]["achternaam"].lower(), r["st"]["voornaam"].lower(), r["st"]["i"])  # noqa: E731
    elif s["uitdraai_sort"] == "Tijd":
        uitdraai_sleutel = lambda r: (r["slot"]["d"], r["slot"]["t"], r["st"]["achternaam"].lower(), r["st"]["i"])  # noqa: E731
    else:
        uitdraai_sleutel = lambda r: (r["slot"]["d"], r["slot"]["lokaal"].lower(), r["slot"]["t"], r["st"]["i"])  # noqa: E731

    rooster = [ROOSTER_KOP]
    uitdraai = [UITDRAAI_KOP]
    for r in sorted(toegewezen.values(), key=rooster_sleutel):
        st, slot = r["st"], r["slot"]
        bijz = []
        if st["ttv"]:
            bijz.append(f"TTV ({s['ttv']} min)")
        if modus == HER and st["eb"] and norm(st["eb"]) == norm(r["beo"]):
            bijz.append("Zelfde beoordelaar als 1e kans")
        if modus == HER and st["ec"] and norm(st["ec"]) == norm(slot["casus"]):
            bijz.append("Zelfde casus als 1e kans")
        for b in bijz[1 if st["ttv"] else 0:]:
            meldingen.append(("Waarschuwing", f"{st['voornaam']} {st['achternaam']}: {b.lower()}."))
        rooster.append([slot["d"], slot["t"] / 1440, slot["lokaal"], slot["casus"], slot["vaardigheid"], r["beo"], r["simu"],
                        st["nr"], st["voornaam"], st["tv"], st["achternaam"], st["klas"], "; ".join(bijz), r["eind"] / 1440])
    for r in sorted(toegewezen.values(), key=uitdraai_sleutel):
        st = r["st"]
        naam = " ".join(x for x in (st["voornaam"], st["tv"], st["achternaam"]) if x)
        tijd = tijd_tekst(r["slot"]["t"])
        uitdraai.append([naam, r["slot"]["lokaal"], f"{datum_tekst(r['slot']['d'])} {tijd}" if s["uitdraai_datum"] == "Ja" else tijd])
    niet = [st for st in volgorde if st["i"] not in toegewezen]
    for st in sorted(niet, key=lambda x: x["i"]):
        rooster.append(["", "", "", "", "", "", "", st["nr"], st["voornaam"], st["tv"], st["achternaam"], st["klas"],
                        "NIET INGEROOSTERD", ""])
        meldingen.append(("Waarschuwing", f"{st['voornaam']} {st['achternaam']} is NIET ingeroosterd: geen vrij lokaal, "
                          "beoordelaar of simucliënt gevonden (let ook op verplichte herkansingsregels)."))

    uit[namen["rooster"]] = rooster
    uit[namen["uitdraai"]] = uitdraai
    if modus == KANS1:
        kop = list(studenten_kop)
        cols = []
        for naam in EERSTE_KOP:
            c = kolom(kop, norm(naam))
            if c < 0:
                c = len(kop)
                kop.append(naam)
            cols.append(c)
        nieuw = [list(r) + [""] * (len(kop) - len(r)) for r in bladen[s["blad_studenten"]]]
        nieuw[0] = kop
        for st in doel:
            r = toegewezen.get(st["i"])
            waarden = [r["slot"]["d"], r["slot"]["t"] / 1440, r["beo"], r["slot"]["casus"]] if r else ["", "", "", ""]
            for c, w in zip(cols, waarden):
                nieuw[st["i"]][c] = w
        uit[s["blad_studenten"]] = nieuw
    info = f"{m['naam']}: {len(toegewezen)} van {len(doel)} studenten ingeroosterd (jaar {s['jaar']}, toets {s['duur']} min, TTV {s['ttv']} min"
    info += f", pauze {tijd_tekst(pv)}-{tijd_tekst(pt)})." if pv is not None else ", geen pauze)."
    meldingen.insert(0, ("Info", info))
    uit[namen["meldingen"]] = [MELDINGEN_KOP] + [list(x) for x in meldingen]
    return {"fouten": [], "meldingen": meldingen, "bladen": uit, "namen": namen}


# ---------------------------------------------------------------- Excel-bestanden (desktop-app)

OPMAAK = {"datum": "dd-mm-yyyy", "eerstedatum": "dd-mm-yyyy", "tijd": "hh:mm", "eindtijd": "hh:mm", "eerstetijd": "hh:mm"}


def excel_waarde(v):
    """openpyxl-waarde -> waarde zoals Excel Online getValues() hem geeft."""
    if isinstance(v, dt.datetime):
        x = v - dt.datetime(1899, 12, 30)
        return x.days + x.seconds / 86400 if x.seconds else x.days
    if isinstance(v, dt.date):
        return (v - dt.date(1899, 12, 30)).days
    if isinstance(v, dt.time):
        return (v.hour * 3600 + v.minute * 60 + v.second) / 86400
    if isinstance(v, dt.timedelta):
        return v.total_seconds() / 86400
    return "" if v is None else v


def lees_werkmap(pad) -> dict:
    from openpyxl import load_workbook
    wb = load_workbook(pad, data_only=True)
    bladen = {}
    for ws in wb.worksheets:
        rijen = [[excel_waarde(c) for c in rij] for rij in ws.iter_rows(values_only=True)]
        while rijen and leeg(rijen[-1]):
            rijen.pop()
        bladen[ws.title] = rijen
    return bladen


def is_studentenblad(rijen: list) -> bool:
    """Het studentenblad herken je aan de kolom EersteDatum; daarvan worden alleen de Eerste*-kolommen geschreven."""
    return bool(rijen) and any(norm(k) == "eerstedatum" for k in rijen[0])


def schrijf_bladen(wb, bladen: dict) -> None:
    """Schrijft matrices in een openpyxl-werkmap (bestaande bladen worden overschreven)."""
    from openpyxl.styles import Font
    tijden = {norm(i["label"]) for i in INSTELLINGEN if i["soort"] == "tijd"}
    for naam, rijen in bladen.items():
        if is_studentenblad(rijen) and naam in wb.sheetnames:
            # Andere cellen (en formules) blijven ongemoeid.
            ws = wb[naam]
            eerste = {norm(k) for k in EERSTE_KOP}
            for c, titel in enumerate(rijen[0], start=1):
                if norm(titel) in eerste:
                    for r, rij in enumerate(rijen, start=1):
                        ws.cell(r, c).value = None if rij[c - 1] == "" else rij[c - 1]
                        if r > 1 and norm(titel) in OPMAAK:
                            ws.cell(r, c).number_format = OPMAAK[norm(titel)]
            continue
        if naam in wb.sheetnames:
            ws = wb[naam]
            ws.delete_rows(1, ws.max_row)
        else:
            ws = wb.create_sheet(naam)
        for rij in rijen:
            ws.append([None if w == "" else w for w in rij])
        kop = rijen[0] if rijen else []
        for c, titel in enumerate(kop, start=1):
            ws.cell(1, c).font = Font(bold=True)
            fmt = OPMAAK.get(norm(titel))
            if fmt and kop != MELDINGEN_KOP:
                for r in range(2, len(rijen) + 1):
                    ws.cell(r, c).number_format = fmt
            breedte = max((len(tekst(rij[c - 1])) for rij in rijen if c - 1 < len(rij)), default=8)
            ws.column_dimensions[ws.cell(1, c).column_letter].width = min(max(breedte, 8) + 2, 90)
        if list(kop) == INSTELLINGEN_KOP:
            for r in range(2, len(rijen) + 1):
                if norm(cel(rijen[r - 1], 0)) in tijden:
                    ws.cell(r, 2).number_format = "hh:mm"
