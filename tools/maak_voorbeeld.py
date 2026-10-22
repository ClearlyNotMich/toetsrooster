"""Maakt voorbeeld/Voorbeeld rooster.xlsx met VERZONNEN gegevens (geen echte studenten)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
import rooster_core as rc  # noqa: E402

DAG1, DAG2 = 46128, 46135  # 16-04-2026 en 23-04-2026


def tijden(van: str, tot: str, stap: int = 10) -> list:
    a, b = rc.naar_minuten(van), rc.naar_minuten(tot)
    return [t / 1440 for t in range(a, b + 1, stap)]


def voorbeeld_bladen() -> dict:
    kop = ["Studentnummer", "Voornaam", "Tussenvoegsel", "Achternaam", "klas", "Niet inroosteren bij SB-docent",
           "Niet inroosteren bij de vaardighedendocent", "TTV", "IsHerkanser", "EersteDatum", "EersteTijd",
           "EersteBeoordelaar", "EersteCasus"]
    s = [kop]
    namen = [("Anna", "", "Jansen", "", "", "Nee"), ("Bas", "de", "Vries", "Ann", "", "Nee"),
             ("Carla", "", "Smit", "", "", "Ja"), ("Daan", "van", "Dijk", "", "Bram", "Nee"),
             ("Eva", "", "Bakker", "", "", "Nee"), ("Fleur", "", "Visser", "Ann; Cor", "", "Nee"),
             ("Gijs", "", "Mulder", "", "", "Ja"), ("Hanna", "", "Bos", "", "", "Nee"),
             ("Ilse", "van der", "Berg", "", "", "Nee"), ("Joris", "", "Meijer", "", "", "Nee"),
             ("Kim", "", "Peters", "", "", "Nee"), ("Lars", "", "Hendriks", "", "", "Nee")]
    for i, (v, tv, a, sb, vd, ttv) in enumerate(namen):
        s.append([900000 + i, v, tv, a, "P2A" if i % 2 else "P2B", sb, vd, ttv, "Nee", "", "", "", ""])
    # Twee herkansers met gegevens van hun eerste kans.
    s.append([900100, "Mila", "", "Koster", "P2A", "", "", "Nee", "Ja", DAG1, 9 * 60 / 1440, "Ann", "XY"])
    s.append([900101, "Noah", "", "Prins", "P2B", "", "", "Ja", "Ja", DAG1, 9 * 60 / 1440, "Bram", "MM"])

    slot_kop = ["Datum", "Tijd", "Lokaal", "Casus", "Vaardigheid", "Casus na pauze"]
    k1 = [slot_kop]
    for lokaal, casus, na, vaardig in (("A", "XY", "BB", "Gesprek"), ("B", "MM", "NN", "Anamnese")):
        k1 += [[DAG1, t, lokaal, casus, vaardig, na] for t in tijden("09:00", "12:30")]
    her = [slot_kop]
    for lokaal, casus, vaardig in (("A", "XY", "Gesprek"), ("B", "MM", "Anamnese")):
        her += [[DAG2, t, lokaal, casus, vaardig, ""] for t in tijden("09:00", "10:30")]

    beo = [["Datum", "Tijd", "Beoordelaar", "Casus"]]
    for naam in ("Ann", "Bram", "Cor"):
        beo += [[DAG1, t, naam, ""] for t in tijden("09:00", "12:30")]
    for naam in ("Ann", "Bram"):
        beo += [[DAG2, t, naam, ""] for t in tijden("09:00", "10:30")]
    simu = [["Datum", "Tijd", "simucliënt", "Casus", "Lokaal"]]
    for naam in ("Sanne", "Tom", "Uma"):
        simu += [[DAG1, t, naam, "", ""] for t in tijden("09:00", "12:30")]
    for naam in ("Sanne", "Tom"):
        simu += [[DAG2, t, naam, "", ""] for t in tijden("09:00", "10:30")]

    inst = rc.instellingen_matrix({"Pauze van": 11 * 60 / 1440, "Pauze tot": 11.5 * 60 / 1440})
    return {"Studenten": s, "Slots_Kans1": k1, "Slots_Her": her, "Beoordelaars": beo, "Simu": simu,
            "Rooster_Kans1": [rc.ROOSTER_KOP], "Rooster_Her": [rc.ROOSTER_KOP], "Instellingen": inst}


def schrijf(pad: Path) -> None:
    from openpyxl import Workbook
    wb = Workbook()
    wb.remove(wb.active)
    rc.schrijf_bladen(wb, voorbeeld_bladen())
    wb.save(pad)


if __name__ == "__main__":
    doel = Path(__file__).resolve().parents[1] / "voorbeeld" / "Voorbeeld rooster.xlsx"
    schrijf(doel)
    print(doel)
