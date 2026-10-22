"""Typecheck van de Office Scripts en: geven ze exact dezelfde uitvoer als de Python-logica?"""
import copy
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import maak_voorbeeld as mv
import rooster_core as rc

ROOT = Path(__file__).resolve().parents[1]
OS = ROOT / "tests" / "officescripts"
SCRIPTS = {"kans1": "OWB Exam Roster Generator.txt", "her": "OWB Retake Exam Roster Generator.txt"}


def test_scripts_zijn_actueel():
    assert subprocess.run([sys.executable, str(ROOT / "tools" / "bouw_scripts.py"), "--check"]).returncode == 0


@pytest.fixture(scope="module")
def gecompileerd(tmp_path_factory):
    tsc = ROOT / "node_modules" / "typescript" / "bin" / "tsc"  # via node: werkt ook op Windows
    assert tsc.exists(), "draai eerst: npm install"
    uit = {}
    for modus, naam in SCRIPTS.items():
        map_ = tmp_path_factory.mktemp(modus)
        shutil.copy(ROOT / naam, map_ / "script.ts")
        r = subprocess.run(["node", str(tsc), "--strict", "--noImplicitAny", "--noEmitOnError", "--target", "es2017",
                            "--lib", "es2017", "--outDir", str(map_ / "js"), str(OS / "excelscript.d.ts"),
                            str(OS / "globals.d.ts"), str(map_ / "script.ts")], capture_output=True, text=True)
        assert r.returncode == 0, r.stdout + r.stderr
        uit[modus] = map_ / "js" / "script.js"
    return uit


def draai(js: Path, bladen: dict, tmp: Path) -> dict:
    (tmp / "in.json").write_text(json.dumps(bladen), encoding="utf-8")
    subprocess.run(["node", str(OS / "harness.js"), str(js), str(tmp / "in.json"), str(tmp / "uit.json")], check=True)
    return json.loads((tmp / "uit.json").read_text(encoding="utf-8"))


def netjes(matrix):
    rijen = []
    for rij in matrix:
        rij = list(rij)
        while rij and rij[-1] in ("", None):
            rij.pop()
        rijen.append(rij)
    while rijen and not rijen[-1]:
        rijen.pop()
    return rijen


def echte_opmaak() -> dict:
    """Zelfde kolomindeling als het echte werkboek (incl. restanten van de oude fout), met verzonnen namen."""
    b = mv.voorbeeld_bladen()
    del b["Instellingen"]
    for rij in b["Studenten"][1:12]:
        rij[8] = 46128  # oude script schreef EersteDatum in IsHerkanser
    b["Studenten"][0][11] = "EersteBeoordelaar\xa0"
    for blad in ("Slots_Kans1", "Slots_Her"):
        b[blad] = [r[:5] for r in b[blad]]  # zonder kolom 'Casus na pauze'
    b["Simu"] = [r + ["", ""] for r in b["Simu"]]
    b["Uitdraai_Kans1"] = [["oude", "inhoud"], ["moet", "weg"], ["x", "y"]] * 10
    return b


def met(**waarden):
    """Voorbeeld met andere instellingen (sleutel -> waarde)."""
    def maak():
        b = mv.voorbeeld_bladen()
        huidig = rc.instellingen_waarden(b["Instellingen"])
        b["Instellingen"] = rc.instellingen_matrix({**huidig, **waarden})
        return b
    return maak


def andere_bladnamen():
    b = met(blad_studenten="Deelnemers", blad_slots1="Tijden 1", blad_slots_her="Tijden 2", blad_beo="Docenten",
            blad_simu="Acteurs", blad_rooster1="R1", blad_rooster_her="R2", blad_uitdraai1="U1",
            blad_uitdraai_her="U2", blad_meldingen="Log")()
    for oud, nieuw in (("Studenten", "Deelnemers"), ("Slots_Kans1", "Tijden 1"), ("Slots_Her", "Tijden 2"),
                       ("Beoordelaars", "Docenten"), ("Simu", "Acteurs")):
        b[nieuw] = b.pop(oud)
    return b


def oude_instellingen():
    b = mv.voorbeeld_bladen()
    b["Instellingen"] = b["Instellingen"][:8]  # alleen de eerste rijen (oudere werkmap)
    b["Instellingen"][7][1] = ""  # TTV-duur jaar 2 leeg -> fout
    return b


def dag_met(**waarden):
    def maak():
        b = mv.dag_bladen()
        b["Instellingen"] = rc.instellingen_matrix({**rc.instellingen_waarden(b["Instellingen"]), **waarden})
        return b
    return maak


def dag_krap():
    b = mv.dag_bladen()
    b["Simu"][5][3] = "12:00"  # Wout alleen 's ochtends
    b["Simu"][4][2] = "14:00"  # Vera pas 's middags
    for rij in b["Toetsdag_Kans1"][1:]:
        rij[3] = rij[2] + "b"
    b["Toetsdag_Kans1"] = b["Toetsdag_Kans1"][:4]
    b["Studenten"][31][7] = "Laat"
    b["Studenten"][32][7] = "Vroeg"
    b["Studenten"][33][7] = "Avond"  # onbekend -> waarschuwing
    return b


def dag_fouten():
    b = mv.dag_bladen()
    b["Toetsdag_Kans1"][1][6] = "Fien"
    b["Toetsdag_Kans1"][5][1] = "C1.33-2"
    b["Simu"][2][2] = "straks"
    return b


def dag_ongeldige_instellingen():
    return dag_met(pauzes="lunch", start="25:00")()


def dag_datumtekst():
    b = mv.dag_bladen()
    for rij, d in zip(b["Toetsdag_Kans1"][1:], ["14-4-26", "di 14 april 2026", "2026-04-14T00:00:00", "14/04/2026", "April 14, 2026"]):
        rij[0] = d
    for rij in b["Simu"][1:6]:
        rij[0] = "14-04-2026 00:00"
    b["Toetsdag_Her"][2][0] = "27 mei"  # zonder jaar -> fout met voorbeeld
    return b


def dag_simu_invoerfouten():
    b = mv.dag_bladen()
    b["Simu"] = [b["Simu"][0]] + [[mv.TOETS, n, "10:00", "17:00"] for n in ("Siem", "Tom", "Uma", "Vera", "Wout", "Siem", "Tom")]
    b["Simu"].append([mv.HER + 1, "Xan", "", ""])
    return b


def concept_met(**waarden):
    def maak():
        b = mv.concept_bladen()
        b["Instellingen"] = rc.instellingen_matrix(waarden)
        return b
    return maak


def concept_studenten_en_fout():
    b = mv.concept_bladen()
    del b["Studenten"]
    i = [k for k, r in enumerate(b["Concept"]) if r[0] == "studenten"][0]
    b["Concept"][i][1] = "Lieve van der Bloemhof"
    b["Concept"].insert(i + 1, ["", "Pim Vos"])
    b["Toetsdag_Her"] = mv.dag_bladen()["Toetsdag_Her"]
    return b


def concept_kapot():
    b = mv.concept_bladen()
    b["Concept"][1][1] = "15 december"
    return b


def concept_vaste_simus(rotatie):
    def maak():
        b = mv.concept_bladen()
        b["Instellingen"] = rc.instellingen_matrix({"simu_rotatie": rotatie})
        b["Simu"][0].append("Vast lokaal")
        for rij, v in zip(b["Simu"][1:], ["C2", "Ja", "Nee", "Z9", "C2", "", "", ""]):
            rij.append(v)
        return b
    return maak


def concept_keuken_en_kan_spelen():
    b = mv.concept_bladen()
    blad = b["Concept"]
    lok = [i for i, r in enumerate(blad) if r[0] == "lokalen"][0]
    cas = [i for i, r in enumerate(blad) if r[0] == "casussen"][0]
    blad[lok + 3][1] = "B2 (keuken)"
    blad[lok + 5][1] = "Praktijkhuis (keuken, tillift)"
    blad[cas][1] = "K1 man (keuken)"
    blad[cas + 2][1] = "K3 vrouw (keuken)"
    blad[cas + 6][1] = "K7 vrouw (keuken; tillift)"
    b["Instellingen"] = rc.instellingen_matrix({"simu_rotatie": "Na elke toets"})
    b["Simu"][0] += ["Vast lokaal", "Kan spelen"]
    for rij, (v, k) in zip(b["Simu"][1:], [("", "man"), ("Ja", "man"), ("", "vrouw"), ("", "vrouw / K1"), ("C2", "man"),
                                           ("", "vrouw"), ("", ""), ("", "")]):
        rij += [v, k]
    return b


def toetsdag_keuken():
    b = mv.dag_bladen()
    b["Toetsdag_Kans1"][5][1] = "C1.39 (keuken)"
    b["Toetsdag_Kans1"][1][2] = "Q 1 (keuken)"
    b["Toetsdag_Kans1"][2][3] = "R 1b (keuken)"  # casus na pauze in een lokaal zonder keuken
    b["Simu"][0].append("Kan spelen")
    for rij, k in zip(b["Simu"][1:], ["Q 1, R 1", "I 1", "", "R 2/Q 2", "x"]):
        rij.append(k)
    return b


def toetsdag_tijden_en_ruilen():
    b = mv.dag_bladen()
    T = mv.TOETS
    kop = b["Toetsdag_Kans1"][0] + ["Beoordelaar 3"]
    b["Toetsdag_Kans1"] = [kop,
                           [T, "A", "Q 1", "", "COPM", "Ann tot 11.15", "Bram 11.45-13.00", "", "Cor vanaf 14.00"],
                           [T, "B", "R 1", "", "COPM", "Dirk tot 13.00", "Eef vanaf 13.00", "", ""],
                           [T, "C", "R 2", "", "COPM", "Eef tot 13.00", "Dirk vanaf 13.00", "", ""],
                           [T, "D", "Q 2", "", "COPM", "Gijs", "Hans", "12.25", ""],
                           [T, "E", "I 1", "", "COPM", "Ann van 14.00 tot 16.00", "", "", ""]]
    return b


def zeven_lokalen(verdelen):
    def maak():
        b = mv.concept_bladen()
        b["Simu"] = b["Simu"][:6] + [b["Simu"][1], b["Simu"][2]]
        for rij in b["Studenten"][1:]:
            rij[5] = rij[6] = ""
        b["Instellingen"] = rc.instellingen_matrix({"verdelen": verdelen})
        return b
    return maak


def toetsdag_kolommen(rijen_):
    def maak():
        b = mv.dag_bladen()
        kop = ["Datum", "Lokaal", "Casus", "Vaardigheid", "Beoordelaar", "Van", "Tot", "Beoordelaar 2", "Van 2", "Tot 2",
               "Beoordelaar 3", "Vanaf 3", "Tot 3"]
        b["Toetsdag_Kans1"] = [kop] + [list(r) + [""] * (len(kop) - len(r)) for r in rijen_]
        return b
    return maak


SCENARIOS = {
    "toetsdag_kolommen_van_tot": toetsdag_kolommen([
        [mv.TOETS, "A", "Q 1", "COPM", "Fien", "", "13:00", "Hans", 13.5 / 24, ""],
        [mv.TOETS, "B", "R 1", "COPM", "Ann tot 12.00", "", "", "Bram", "12:00", "", "Ann", "15:40", ""],
        [mv.TOETS, "C", "R 2", "COPM", "Bram", "", "12.00", "Cor", "13.00", "15:15", "Dirk", "15:40", ""],
        [mv.TOETS, "D", "Q 2", "COPM", "Gijs tot 11.00", "", "16:00"]]),
    "toetsdag_kolommen_fout": toetsdag_kolommen([
        [mv.TOETS, "A", "Q 1", "COPM", "Fien", "", "13u"],
        [mv.TOETS, "B", "R 1", "COPM", "Ann", "14:00", "13:00"]]),
    "toetsdag_tijden_en_ruilen": toetsdag_tijden_en_ruilen,
    "zeven_lokalen_evenredig": zeven_lokalen("Evenredig"),
    "zeven_lokalen_op_volgorde": zeven_lokalen("Op volgorde"),
    "concept_keuken_en_kan_spelen": concept_keuken_en_kan_spelen,
    "toetsdag_keuken": toetsdag_keuken,
    "concept_vast_na_elke_toets": concept_vaste_simus("Na elke toets"),
    "concept_vast_na_elke_pauze": concept_vaste_simus("Na elke pauze"),
    "concept": mv.concept_bladen,
    "concept_na_elke_toets": concept_met(simu_rotatie="Na elke toets", casus_na="Na elke pauze afwisselen"),
    "concept_oude_waarde_ja": concept_met(simu_rotatie="Ja"),
    "concept_studenten_en_fout": concept_studenten_en_fout,
    "concept_kapot": concept_kapot,
    "dag_simu_invoerfouten": dag_simu_invoerfouten,
    "dag_datumtekst": dag_datumtekst,
    "dag": mv.dag_bladen,
    "dag_anders": dag_met(simu_rotatie="Nee", casus_na="Na elke pauze afwisselen", ttv_plek="Zo vroeg mogelijk",
                          ttv_eerst="Nee", vrije_plekken="Nee", wissel=10, pauzes="12:30-13:15", middag="13:00",
                          her_beo="Verplicht", rooster_sort="Tijd, dan lokaal"),
    "dag_krap": dag_krap,
    "dag_fouten": dag_fouten,
    "dag_ongeldige_instellingen": dag_ongeldige_instellingen,
    "alles_anders": met(jaar=2, duur2=20, ttv2=30, casus_na="Nee", ttv_plek="Zo vroeg mogelijk", ttv_eerst="Nee",
                        deelnaam="nee", her_beo="Verplicht", her_casus="Maakt niet uit", rooster_sort="Tijd, dan lokaal",
                        uitdraai_sort="Tijd", uitdraai_datum="Nee"),
    "uitdraai_lokaal": met(uitdraai_sort="Lokaal, dan tijd", her_casus="Verplicht"),
    "andere_bladnamen": andere_bladnamen,
    "oude_instellingen": oude_instellingen,
    "foute_instelling": met(rooster_sort="Willekeurig", jaar=3),
    "voorbeeld": mv.voorbeeld_bladen,
    "echte_opmaak": echte_opmaak,
    "fout": lambda: {**mv.voorbeeld_bladen(), "Simu": [["Datum", "Tijd"]]},
    "krap": lambda: {**mv.voorbeeld_bladen(), "Slots_Kans1": mv.voorbeeld_bladen()["Slots_Kans1"][:6],
                     "Slots_Her": mv.voorbeeld_bladen()["Slots_Her"][:2]},
}


@pytest.mark.parametrize("modus", ["kans1", "her"])
@pytest.mark.parametrize("scenario", list(SCENARIOS))
def test_zelfde_uitvoer_als_python(gecompileerd, tmp_path, modus, scenario):
    bladen = SCENARIOS[scenario]()
    verwacht = copy.deepcopy(bladen)
    resultaat = rc.maak_rooster(copy.deepcopy(bladen), modus)
    verwacht.update(resultaat["bladen"])
    uit = draai(gecompileerd[modus], bladen, tmp_path)
    assert set(uit["bladen"]) == set(verwacht)
    for naam in verwacht:
        assert netjes(uit["bladen"][naam]) == netjes(verwacht[naam]), naam
    assert uit["actief"] == resultaat["namen"]["meldingen" if resultaat["fouten"] else "rooster"]
