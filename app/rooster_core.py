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
MODI = {
    KANS1: {"naam": "Eerste kans", "slots": "Slots_Kans1", "rooster": "Rooster_Kans1", "uitdraai": "Uitdraai_Kans1"},
    HER: {"naam": "Herkansing", "slots": "Slots_Her", "rooster": "Rooster_Her", "uitdraai": "Uitdraai_Her"},
}
ROOSTER_KOP = ["Datum", "Tijd", "Lokaal", "Casus", "Vaardigheid", "Beoordelaar", "simucliënt", "stnr",
               "Voornaam", "vv", "Achternaam", "klas", "bijzheden", "Eindtijd"]
UITDRAAI_KOP = ["Naam", "Lokaal", "Tijd"]
MELDINGEN_KOP = ["Soort", "Melding"]
EERSTE_KOP = ["EersteDatum", "EersteTijd", "EersteBeoordelaar", "EersteCasus"]
# (label, standaardwaarde, toelichting) — het blad Instellingen gebruikt exact deze labels.
INSTELLINGEN = [
    ("Jaar", 1, "Studiejaar van deze toets (1 of 2); bepaalt welke toetsduur hieronder geldt."),
    ("Toetsduur jaar 1 (min)", 10, "Duur van een gewone toets in jaar 1 (= één slot van 10 minuten)."),
    ("TTV-toetsduur jaar 1 (min)", 15, "Duur voor studenten met TTV (toegestane tijdverlenging) in jaar 1."),
    ("Toetsduur jaar 2 (min)", 10, "Duur van een gewone toets in jaar 2 (pas aan: jaar 2 heeft een andere tijd)."),
    ("TTV-toetsduur jaar 2 (min)", 15, "Duur voor studenten met TTV in jaar 2."),
    ("Pauze van", "", "Begin van de pauze (bijv. 12:00). Leeg = geen pauze."),
    ("Pauze tot", "", "Einde van de pauze (bijv. 12:30). Leeg = geen pauze."),
]


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


def beperkt(naam: str, verboden: list[str]) -> bool:
    # Zoals het oude script: ook deels overeenkomende namen tellen (spelfouten).
    n = naam.strip().lower()
    return any(n == v.lower() or v.lower() in n or n in v.lower() for v in verboden)


def leeg(rij: list) -> bool:
    return all(tekst(x) == "" for x in rij)


# ---------------------------------------------------------------- inlezen

def instellingen_waarden(matrix: list | None) -> dict:
    """Label -> waarde uit blad Instellingen (standaardwaarde als de rij ontbreekt)."""
    waarden = {label: standaard for label, standaard, _ in INSTELLINGEN}
    labels = {norm(label): label for label in waarden}
    for rij in (matrix or [])[1:]:
        if norm(cel(rij, 0)) in labels:
            waarden[labels[norm(cel(rij, 0))]] = cel(rij, 1)
    return waarden


def lees_instellingen(matrix: list | None, fouten: list) -> dict:
    w = instellingen_waarden(matrix)
    s = {"jaar": int(tekst(w["Jaar"])) if tekst(w["Jaar"]).isdigit() else 0}
    if s["jaar"] not in (1, 2):
        fouten.append("Instellingen: 'Jaar' moet 1 of 2 zijn.")
        s["jaar"] = 1
    for sleutel, label in (("duur", "Toetsduur jaar {} (min)"), ("ttv", "TTV-toetsduur jaar {} (min)")):
        label = label.format(s["jaar"])
        s[sleutel] = int(tekst(w[label])) if tekst(w[label]).isdigit() else 0
        if s[sleutel] <= 0:
            fouten.append(f"Instellingen: '{label}' moet een positief aantal minuten zijn.")
    van, tot = w["Pauze van"], w["Pauze tot"]
    s["pauze_van"] = s["pauze_tot"] = None
    if tekst(van) or tekst(tot):
        a, b = naar_minuten(van), naar_minuten(tot)
        if a is None or b is None or a >= b:
            fouten.append("Instellingen: vul 'Pauze van' en 'Pauze tot' allebei in als tijd (van < tot), of laat beide leeg.")
        else:
            s["pauze_van"], s["pauze_tot"] = a, b
    return s


def lees_studenten(matrix: list | None, fouten: list, meldingen: list) -> tuple[list, list]:
    if not matrix:
        fouten.append("Blad 'Studenten' ontbreekt of is leeg.")
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
            fouten.append(f"Blad 'Studenten': kolom '{naam.capitalize()}' ontbreekt.")
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
        meldingen.append(("Waarschuwing", f"Studenten rij {', '.join(oud)}: 'IsHerkanser' bevat een getal/datum "
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
    """Berekent het rooster. Geeft {'fouten', 'meldingen', 'bladen'} terug.

    'bladen' bevat de nieuwe inhoud van Rooster_*, Uitdraai_*, Meldingen en
    (alleen bij eerste kans) Studenten. Bij fouten wordt alleen Meldingen gevuld.
    """
    m = MODI[modus]
    nieuw_blad = {} if bladen.get("Instellingen") else {"Instellingen": instellingen_matrix()}
    fouten: list[str] = []
    meldingen: list[tuple[str, str]] = []
    s = lees_instellingen(bladen.get("Instellingen"), fouten)
    studenten, studenten_kop = lees_studenten(bladen.get("Studenten"), fouten, meldingen)
    slots = lees_slots(bladen.get(m["slots"]), m["slots"], fouten)
    beoordelaars = lees_beschikbaar(bladen.get("Beoordelaars"), "Beoordelaars", ("beoordelaar", "naam"), fouten)
    simus = lees_beschikbaar(bladen.get("Simu"), "Simu", ("simuclint", "simu", "simulant", "naam"), fouten)
    if fouten:
        rijen = [MELDINGEN_KOP] + [["Fout", f] for f in fouten] + [list(x) for x in meldingen]
        rijen.append(["Info", f"{m['naam']}: rooster NIET aangepast door bovenstaande fouten."])
        return {"fouten": fouten, "meldingen": meldingen, "bladen": {**nieuw_blad, "Meldingen": rijen}}

    pv, pt = s["pauze_van"], s["pauze_tot"]
    na_pauze = lambda t: pv is not None and t >= pt  # noqa: E731
    bruikbaar = []
    in_pauze = 0
    for slot in slots:
        if pv is not None and pv <= slot["t"] < pt:
            in_pauze += 1
            continue
        if na_pauze(slot["t"]) and slot["casus_na"]:
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
    volgorde = [st for st in doel if st["ttv"]] + [st for st in doel if not st["ttv"]]
    gewoon = sorted(bruikbaar, key=lambda x: (x["d"], x["t"], x["n"]))
    # TTV: liefst het laatste slot van een blok vóór de pauze, zodat de extra tijd in de pauze valt.
    ttv_volgorde = sorted(bruikbaar, key=lambda x: (x["d"], 1 if na_pauze(x["t"]) else 0, -x["t"], x["n"]))
    bezet: dict = {}

    def vrij(sleutel, a, b):
        return all(b <= x or a >= y for x, y in bezet.get(sleutel, []))

    def kies(lijst, slot, a, b, soort, st, strikt):
        for kandidaat in lijst:
            if kandidaat["casus"] and norm(kandidaat["casus"]) != norm(slot["casus"]):
                continue
            if kandidaat["lokaal"] and norm(kandidaat["lokaal"]) != norm(slot["lokaal"]):
                continue
            if soort == "b" and beperkt(kandidaat["naam"], st["verboden"]):
                continue
            if soort == "b" and strikt and st["eb"] and norm(kandidaat["naam"]) == norm(st["eb"]):
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
            if strikt and st["ec"] and norm(slot["casus"]) == norm(st["ec"]):
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

    rooster = [ROOSTER_KOP]
    uitdraai = [UITDRAAI_KOP]
    for r in sorted(toegewezen.values(), key=lambda r: (r["slot"]["d"], r["slot"]["lokaal"].lower(), r["slot"]["t"], r["slot"]["n"])):
        st, slot = r["st"], r["slot"]
        bijz = []
        if st["ttv"]:
            bijz.append(f"TTV ({s['ttv']} min)")
        if modus == HER and st["eb"] and norm(st["eb"]) == norm(r["beo"]):
            bijz.append("Zelfde beoordelaar als 1e kans")
        if modus == HER and st["ec"] and norm(st["ec"]) == norm(slot["casus"]):
            bijz.append("Zelfde casus als 1e kans")
        for b in bijz[1 if st["ttv"] else 0:]:
            meldingen.append(("Waarschuwing", f"{st['voornaam']} {st['achternaam']}: {b.lower()} (geen andere optie gevonden)."))
        rooster.append([slot["d"], slot["t"] / 1440, slot["lokaal"], slot["casus"], slot["vaardigheid"], r["beo"], r["simu"],
                        st["nr"], st["voornaam"], st["tv"], st["achternaam"], st["klas"], "; ".join(bijz), r["eind"] / 1440])
    for r in sorted(toegewezen.values(), key=lambda r: (r["st"]["achternaam"].lower(), r["st"]["voornaam"].lower(), r["st"]["i"])):
        st = r["st"]
        naam = " ".join(x for x in (st["voornaam"], st["tv"], st["achternaam"]) if x)
        uitdraai.append([naam, r["slot"]["lokaal"], f"{datum_tekst(r['slot']['d'])} {tijd_tekst(r['slot']['t'])}"])
    niet = [st for st in volgorde if st["i"] not in toegewezen]
    for st in sorted(niet, key=lambda x: x["i"]):
        rooster.append(["", "", "", "", "", "", "", st["nr"], st["voornaam"], st["tv"], st["achternaam"], st["klas"],
                        "NIET INGEROOSTERD", ""])
        meldingen.append(("Waarschuwing", f"{st['voornaam']} {st['achternaam']} is NIET ingeroosterd: geen vrij lokaal, beoordelaar of simucliënt gevonden."))

    uit = {**nieuw_blad, m["rooster"]: rooster, m["uitdraai"]: uitdraai}
    if modus == KANS1:
        nieuw = [list(r) for r in bladen["Studenten"]]
        kop = list(studenten_kop)
        cols = []
        for naam in EERSTE_KOP:
            c = kolom(kop, norm(naam))
            if c < 0:
                c = len(kop)
                kop.append(naam)
            cols.append(c)
        breedte = len(kop)
        nieuw = [r + [""] * (breedte - len(r)) for r in nieuw]
        nieuw[0] = kop
        for st in doel:
            r = toegewezen.get(st["i"])
            waarden = [r["slot"]["d"], r["slot"]["t"] / 1440, r["beo"], r["slot"]["casus"]] if r else ["", "", "", ""]
            for c, w in zip(cols, waarden):
                nieuw[st["i"]][c] = w
        uit["Studenten"] = nieuw
    info = f"{m['naam']}: {len(toegewezen)} van {len(doel)} studenten ingeroosterd (jaar {s['jaar']}, toets {s['duur']} min, TTV {s['ttv']} min"
    info += f", pauze {tijd_tekst(pv)}-{tijd_tekst(pt)})." if pv is not None else ", geen pauze)."
    meldingen.insert(0, ("Info", info))
    uit["Meldingen"] = [MELDINGEN_KOP] + [list(x) for x in meldingen]
    return {"fouten": [], "meldingen": meldingen, "bladen": uit}


def instellingen_matrix(waarden: dict | None = None) -> list:
    """Blad Instellingen met standaardwaarden of de gegeven label -> waarde."""
    return [["Instelling", "Waarde", "Toelichting"]] + [
        [label, (waarden or {}).get(label, standaard), uitleg] for label, standaard, uitleg in INSTELLINGEN]


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


def schrijf_bladen(wb, bladen: dict) -> None:
    """Schrijft matrices in een openpyxl-werkmap (bestaande bladen worden overschreven)."""
    from openpyxl.styles import Font
    for naam, rijen in bladen.items():
        if naam == "Studenten" and naam in wb.sheetnames:
            # Alleen de Eerste*-kolommen: andere cellen (en formules) blijven ongemoeid.
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
            if fmt and naam not in ("Meldingen",):
                for r in range(2, len(rijen) + 1):
                    ws.cell(r, c).number_format = fmt
            breedte = max((len(tekst(rij[c - 1])) for rij in rijen if c - 1 < len(rij)), default=8)
            ws.column_dimensions[ws.cell(1, c).column_letter].width = min(max(breedte, 8) + 2, 90)
        if naam == "Instellingen":
            for r in range(2, len(rijen) + 1):
                if norm(cel(rijen[r - 1], 0)).startswith("pauze"):
                    ws.cell(r, 2).number_format = "hh:mm"
