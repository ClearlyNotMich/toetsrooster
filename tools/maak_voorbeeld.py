"""Voorbeeldwerkmappen met VERZONNEN gegevens (geen echte studenten of medewerkers).

- dag_bladen(): de gewone werkwijze (blad Toetsdag + Simu per dag), nagebouwd naar een echte toetsdag:
  5 lokalen, 4 blokken, 3 pauzes, 5 simu's, één beoordelaarswissel, 61 studenten (1 TTV, 1 ochtendwens),
  uitsluitingen per klas. Dit is 'voorbeeld/Voorbeeld rooster.xlsx'.
- voorbeeld_bladen(): de oude werkwijze (één rij per slot in Slots_*/Beoordelaars/Simu).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
import rooster_core as rc  # noqa: E402

DAG1, DAG2 = 46128, 46135  # oude werkwijze: 16-04-2026 en 23-04-2026
TOETS, HER = 46126, 46169  # toetsdag: 14-04-2026 en 27-05-2026
VOORNAMEN = ["Abel", "Bas", "Carla", "Daan", "Eva", "Fleur", "Hanna", "Ilse", "Joris", "Cato", "Lars", "Mila",
             "Otto", "Olaf", "Puck", "Quinn", "Roos", "Tijn", "Tess", "Ugo"]
ACHTERNAMEN = ["Appelboom", "Vries", "Smit", "Dijk", "Bloemhof", "Vlinderhof", "Duinkerk", "Bos", "Berg", "Molenwiek", "Peters",
               "Hendriks", "Koster", "Prins", "Kok", "Vos", "Post", "Kuiper", "Wit", "Brink"]


def tijden(van: str, tot: str, stap: int = 10) -> list:
    a, b = rc.naar_minuten(van), rc.naar_minuten(tot)
    return [t / 1440 for t in range(a, b + 1, stap)]


def dag_bladen() -> dict:
    kop = ["Studentnummer", "Roepnaam", "Tussenvoegsel", "Achternaam", "Klas p2", "Niet inroosteren bij SB-docent P2",
           "Niet inroosteren bij de vaardighedendocent", "Voorkeur", "Opmerkingen", "IsHerkanser"] + rc.EERSTE_KOP
    s = [kop]
    # Klas A mag bij iedereen, B niet bij Ann/Bram, C niet bij Bram en Eef (schrijfwijze met '/').
    klassen = [("P2A", "Gijs", "Hans Hoek"), ("P2B", "Ann", "Bram Bos"), ("P2C", "Bram/Eef", "Gijs Goud")]
    for i in range(61):
        klas, sb, vd = klassen[0 if i < 23 else 1 if i < 44 else 2]
        opm = {0: "ttv nodig", 1: "liefst ochtend, zo vroeg mogelijk"}.get(i, "")
        s.append([900000 + i, VOORNAMEN[i % 20], "van" if i % 7 == 3 else "", ACHTERNAMEN[(i * 7) % 20] + ("" if i < 20 else str(i)),
                  klas, sb, vd, "Middag" if i == 30 else "", opm, "Nee", "", "", "", ""])
    s.append([900100, "Mila", "", "Herkansing", "P2A", "", "", "", "", "Ja", TOETS, 9 * 60 / 1440, "Ann", "Q 1"])
    s.append([900101, "Otto", "", "Herkansing", "P2B", "", "", "", "ttv", "Ja", TOETS, 9 * 60 / 1440, "Bram", "R 1"])

    dag_kop = ["Datum", "Lokaal", "Casus", "Casus na pauze", "Vaardigheid", "Beoordelaar", "Beoordelaar 2", "Wissel om"]
    k1 = [dag_kop,
          [TOETS, "C1.33-1", "Q 1", "", "COPM", "Ann", "", ""],
          [TOETS, "C1.33-2", "R 1", "", "COPM", "Bram", "", ""],
          [TOETS, "C1.23-1", "R 2", "", "Activiteitenweger", "Cor", "", ""],
          [TOETS, "C1.23-2", "Q 2", "", "Activiteitenweger", "Dirk", "", ""],
          [TOETS, "C1.39", "I 1", "", "COPM", "Eef", "Fien", "12:25"]]
    her = [dag_kop,
           [HER, "C1.33-1", "Q 1", "R 1", "COPM", "Ann", "", ""],
           [HER, "C1.33-2", "R 2", "", "COPM", "Bram", "", ""]]
    simu = [["Datum", "simucliënt", "Vanaf", "Tot"]] + [[TOETS, n, "", ""] for n in ("Siem", "Tom", "Uma", "Vera", "Wout")]
    simu += [[HER, "Siem", "", ""], [HER, "Tom", "", ""], [HER, "Uma", "", "12:00"]]
    return {"Studenten": s, "Toetsdag_Kans1": k1, "Toetsdag_Her": her, "Simu": simu,
            "Instellingen": rc.instellingen_matrix()}


def concept_blad(datum=46371) -> list:
    """Conceptblad in lijstvorm, zoals de roostermaker het opschrijft (verzonnen namen)."""
    rijen = [["jaar 1 toets", ""], ["datum ", datum]]
    secties = [
        ("inzet", ["Ann", "Bram", "Cor", "Dirk", "Eef", "Gijs", "Fien ochtend tot 13.00", "Hans middag vanaf 13.30 uur",
                   "Ida (reactie nog afwachten)", "Jet (nog niet eerder gedaan)"]),
        ("tijden", ["10.00 - 10.15", "10.20 - 10.35", "10.40 - 10.55", "10.40 - 10.55", "11.00 - 11.15", "11.45 - 12.00",
                    "12.05 - 12.20", "12.25 - 12.40", "12.45 - 13.00", "14.00 - 14.15", "14.20 - 14.35", "14.40 - 14.55",
                    "15.00 - 15.15", "15.45 - 16.00", "16.05 - 16.20", "16.25 - 16.40", "16.45 - 17.00"]),
        ("pauzes", ["11.15-11.40", "13.00-13.55", "15.15-15.40"]),
        ("lokalen", ["A1", "A2", "B1", "B2", "C1", "Praktijkhuis", "C2"]),
        ("casussen", ["K1 man", "K2 man", "K3 vrouw", "K4 vrouw", "K5 vrouw", "K6 vrouw", "K7 vrouw"]),
        ("simu's", ["7 x"]),
        ("studenten", []),
    ]
    for kop, waarden in secties:
        rijen.append([kop, waarden[0] if waarden else ""])
        rijen += [["", w] for w in waarden[1:]]
    return rijen


def concept_bladen() -> dict:
    """Werkmap met conceptblad + studenten + simu's voor die dag (8 beschikbaar, 7 nodig)."""
    b = dag_bladen()
    simu = [["Datum", "simucliënt", "Vanaf", "Tot"]] + [[46371, n, "10:00", "17:00"]
                                                       for n in ("Siem", "Tom", "Uma", "Vera", "Wout", "Xan", "Yara", "Zeger")]
    return {"Concept": concept_blad(), "Studenten": b["Studenten"], "Simu": simu, "Instellingen": rc.instellingen_matrix()}


def voorbeeld_bladen() -> dict:
    kop = ["Studentnummer", "Voornaam", "Tussenvoegsel", "Achternaam", "klas", "Niet inroosteren bij SB-docent",
           "Niet inroosteren bij de vaardighedendocent", "TTV", "IsHerkanser", "EersteDatum", "EersteTijd",
           "EersteBeoordelaar", "EersteCasus"]
    s = [kop]
    namen = [("Abel", "", "Appelboom", "", "", "Nee"), ("Bas", "de", "Vries", "Ann", "", "Nee"),
             ("Carla", "", "Smit", "", "", "Ja"), ("Daan", "van", "Dijk", "", "Bram", "Nee"),
             ("Eva", "", "Bloemhof", "", "", "Nee"), ("Fleur", "", "Vlinderhof", "Ann; Cor", "", "Nee"),
             ("Gijs", "", "Duinkerk", "", "", "Ja"), ("Hanna", "", "Bos", "", "", "Nee"),
             ("Ilse", "van der", "Berg", "", "", "Nee"), ("Joris", "", "Molenwiek", "", "", "Nee"),
             ("Cato", "", "Peters", "", "", "Nee"), ("Lars", "", "Hendriks", "", "", "Nee")]
    for i, (v, tv, a, sb, vd, ttv) in enumerate(namen):
        s.append([900000 + i, v, tv, a, "P2A" if i % 2 else "P2B", sb, vd, ttv, "Nee", "", "", "", ""])
    # Twee herkansers met gegevens van hun eerste kans.
    s.append([900100, "Mila", "", "Koster", "P2A", "", "", "Nee", "Ja", DAG1, 9 * 60 / 1440, "Ann", "XY"])
    s.append([900101, "Otto", "", "Prins", "P2B", "", "", "Ja", "Ja", DAG1, 9 * 60 / 1440, "Bram", "MM"])

    slot_kop = ["Datum", "Tijd", "Lokaal", "Casus", "Vaardigheid", "Casus na pauze"]
    k1 = [slot_kop]
    for lokaal, casus, na, vaardig in (("A", "XY", "BB", "Gesprek"), ("B", "MM", "NN", "Anamnese")):
        # Kort ochtendblok, zodat er ook na de pauze (11:00-11:30) studenten zijn.
        k1 += [[DAG1, t, lokaal, casus, vaardig, na] for t in tijden("10:20", "12:30")]
    her = [slot_kop]
    for lokaal, casus, vaardig in (("A", "XY", "Gesprek"), ("B", "MM", "Anamnese")):
        her += [[DAG2, t, lokaal, casus, vaardig, ""] for t in tijden("09:00", "10:30")]

    beo = [["Datum", "Tijd", "Beoordelaar", "Casus"]]
    for naam in ("Ann", "Bram", "Cor"):
        beo += [[DAG1, t, naam, ""] for t in tijden("09:00", "12:30")]
    for naam in ("Ann", "Bram"):
        beo += [[DAG2, t, naam, ""] for t in tijden("09:00", "10:30")]
    simu = [["Datum", "Tijd", "simucliënt", "Casus", "Lokaal"]]
    for naam in ("Siem", "Tom", "Uma"):
        simu += [[DAG1, t, naam, "", ""] for t in tijden("09:00", "12:30")]
    for naam in ("Siem", "Tom"):
        simu += [[DAG2, t, naam, "", ""] for t in tijden("09:00", "10:30")]

    inst = rc.instellingen_matrix({"pauzes": "11:00-11:30", "duur1": 10, "ttv1": 15, "duur2": 10, "ttv2": 15,
                                   "vrije_plekken": "Nee"})
    return {"Studenten": s, "Slots_Kans1": k1, "Slots_Her": her, "Beoordelaars": beo, "Simu": simu,
            "Rooster_Kans1": [rc.ROOSTER_KOP], "Rooster_Her": [rc.ROOSTER_KOP], "Instellingen": inst}


def voorbeeld_werkmap() -> dict:
    """De voorbeeldwerkmap zoals gebruikers hem zien: blad Toetsdag met Van/Tot per beoordelaar, blad Simu met de
    kolommen Vast lokaal en Kan spelen (leeg). Zelfde rooster als dag_bladen()."""
    b = dag_bladen()
    kop = ["Datum", "Lokaal", "Casus", "Casus na pauze", "Vaardigheid", "Beoordelaar", "Van", "Tot",
           "Beoordelaar 2", "Van 2", "Tot 2"]
    for naam in ("Toetsdag_Kans1", "Toetsdag_Her"):
        rijen = [kop]
        for d, lokaal, casus, na, vaardig, b1, b2, wissel in b[naam][1:]:
            rijen.append([d, lokaal, casus, na, vaardig, b1, "", wissel, b2, wissel, ""])
        b[naam] = rijen
    b["Simu"] = [b["Simu"][0] + ["Vast lokaal", "Kan spelen"]] + [r + ["", ""] for r in b["Simu"][1:]]
    return b


def schrijf(pad: Path, bladen: dict | None = None) -> None:
    from openpyxl import Workbook
    wb = Workbook()
    wb.remove(wb.active)
    rc.schrijf_bladen(wb, bladen or dag_bladen())
    wb.save(pad)


if __name__ == "__main__":
    doel = Path(__file__).resolve().parents[1] / "voorbeeld" / "Voorbeeld rooster.xlsx"
    schrijf(doel, voorbeeld_werkmap())
    print(doel)
