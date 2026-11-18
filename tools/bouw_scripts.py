"""Maakt de twee Office Scripts (.txt) uit officescripts/rooster.ts en de tabel met instellingen in docs/REGELS.md.
`--check`: faalt als ze verouderd zijn."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))
from rooster_core import INSTELLINGEN, toelichting  # noqa: E402
DOELEN = {
    "OWB Exam Roster Generator.txt": {"__MODUS__": "kans1", "__MODUS_NAAM__": "EERSTE KANS", "__SLOTS__": "Slots_Kans1", "__DAG__": "Toetsdag_Kans1",
        "__ROOSTER__": "Rooster_Kans1", "__UITDRAAI__": "Uitdraai_Kans1",
        "__EXTRA__": ",\n *           EersteDatum/EersteTijd/EersteBeoordelaar/EersteCasus in Studenten"},
    "OWB Retake Exam Roster Generator.txt": {"__MODUS__": "her", "__MODUS_NAAM__": "HERKANSING", "__SLOTS__": "Slots_Her", "__DAG__": "Toetsdag_Her",
        "__ROOSTER__": "Rooster_Her", "__UITDRAAI__": "Uitdraai_Her", "__EXTRA__": ""},
}


def inhoud(vervang: dict) -> str:
    tekst = (ROOT / "officescripts" / "rooster.ts").read_text(encoding="utf-8")
    # Instellingen-schema uit Python, één regel per instelling.
    schema = "[\n" + "".join(f"    {json.dumps(i, ensure_ascii=False)},\n" for i in INSTELLINGEN) + "]"
    for oud, nieuw in {**vervang, "__INSTELLINGEN__": schema}.items():
        tekst = tekst.replace(oud, nieuw)
    return tekst


def regels() -> str:
    # Alles na de markering in docs/REGELS.md is de tabel met instellingen.
    markering = "<!-- tabel: gegenereerd uit rooster_core.INSTELLINGEN -->\n"
    tekst = (ROOT / "docs" / "REGELS.md").read_text(encoding="utf-8")
    if any(not r.startswith("|") for r in tekst[tekst.index(markering) + len(markering):].splitlines()):
        sys.exit("docs/REGELS.md: na de tabel met instellingen staat nog tekst; zet die boven de markering, "
                 "anders gaat hij verloren. Er is niets geschreven.")
    rijen = [f"| {i['groep']} | {i['label']} | {i['standaard']} | {toelichting(i) or 'Naam van het blad.'} |\n" for i in INSTELLINGEN]
    return tekst[:tekst.index(markering) + len(markering)] + "| Groep | Instelling | Standaard | Uitleg |\n|---|---|---|---|\n" + "".join(rijen)


if __name__ == "__main__":
    fout = False
    for naam, nieuw in [*((naam, inhoud(vervang)) for naam, vervang in DOELEN.items()), ("docs/REGELS.md", regels())]:
        pad = ROOT / naam
        if "--check" in sys.argv:
            if not pad.exists() or pad.read_text(encoding="utf-8") != nieuw:
                print(f"VEROUDERD: {naam} (draai python tools/bouw_scripts.py)")
                fout = True
        else:
            pad.write_text(nieuw, encoding="utf-8")
            print(pad)
    sys.exit(1 if fout else 0)
