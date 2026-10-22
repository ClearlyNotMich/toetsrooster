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
    b["Instellingen"] = b["Instellingen"][:8]  # alleen de rijen van de vorige versie
    b["Instellingen"][7][1] = ""  # pauze tot leeg -> fout: beide of geen
    return b


SCENARIOS = {
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
