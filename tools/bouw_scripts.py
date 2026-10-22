"""Maakt de twee Office Scripts (.txt) uit officescripts/rooster.ts. `--check`: faalt als ze verouderd zijn."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOELEN = {
    "OWB Exam Roster Generator.txt": {"__MODUS__": "kans1", "__MODUS_NAAM__": "EERSTE KANS", "__SLOTS__": "Slots_Kans1",
        "__ROOSTER__": "Rooster_Kans1", "__UITDRAAI__": "Uitdraai_Kans1",
        "__EXTRA__": ",\n *           EersteDatum/EersteTijd/EersteBeoordelaar/EersteCasus in Studenten"},
    "OWB Retake Exam Roster Generator.txt": {"__MODUS__": "her", "__MODUS_NAAM__": "HERKANSING", "__SLOTS__": "Slots_Her",
        "__ROOSTER__": "Rooster_Her", "__UITDRAAI__": "Uitdraai_Her", "__EXTRA__": ""},
}


def inhoud(vervang: dict) -> str:
    tekst = (ROOT / "officescripts" / "rooster.ts").read_text(encoding="utf-8")
    for oud, nieuw in vervang.items():
        tekst = tekst.replace(oud, nieuw)
    return tekst


if __name__ == "__main__":
    fout = False
    for naam, vervang in DOELEN.items():
        pad, nieuw = ROOT / naam, inhoud(vervang)
        if "--check" in sys.argv:
            if not pad.exists() or pad.read_text(encoding="utf-8") != nieuw:
                print(f"VEROUDERD: {naam} (draai python tools/bouw_scripts.py)")
                fout = True
        else:
            pad.write_text(nieuw, encoding="utf-8")
            print(pad)
    sys.exit(1 if fout else 0)
