"""Rooktest van de Qt-app zonder scherm: openen, rooster maken, opslaan als Excel en PDF."""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from openpyxl import load_workbook  # noqa: E402

import maak_voorbeeld as mv  # noqa: E402
import rooster_core as rc  # noqa: E402
import roosterapp  # noqa: E402


def test_app_maakt_en_bewaart(tmp_path):
    bron = tmp_path / "werkmap.xlsx"
    mv.schrijf(bron)
    assert roosterapp.controle(str(bron), str(tmp_path)) == 0
    uit = rc.lees_werkmap(tmp_path / "controle-Rooster_Kans1.xlsx")
    verwacht = rc.maak_rooster(rc.lees_werkmap(bron), "kans1")["bladen"]
    for blad in ("Rooster_Kans1", "Uitdraai_Kans1"):
        assert [[round(c, 6) if isinstance(c, float) else c for c in r] for r in uit[blad]] == \
               [[round(c, 6) if isinstance(c, float) else ("" if c is None else c) for c in r] for r in verwacht[blad]]
    # Studenten: alleen Eerste*-kolommen veranderd, rest identiek
    oud, nieuw = rc.lees_werkmap(bron)["Studenten"], uit["Studenten"]
    assert [r[:9] for r in oud] == [r[:9] for r in nieuw]
    assert load_workbook(tmp_path / "controle-Rooster_Kans1.xlsx")["Rooster_Kans1"]["B2"].number_format == "hh:mm"
    for naam in ("controle-Rooster_Kans1.pdf", "controle-Rooster_Her.pdf", "controle-Rooster_Kans1-docenten.pdf"):
        assert (tmp_path / naam).read_bytes()[:4] == b"%PDF"
    sjabloon = rc.lees_werkmap(tmp_path / "controle-sjabloon.xlsx")
    assert set(sjabloon) == {"Studenten", "Slots_Kans1", "Slots_Her", "Beoordelaars", "Simu", "Instellingen"}
    assert rc.maak_rooster(sjabloon, "kans1")["fouten"] == []  # leeg maar geldig
    assert len(rc.lees_werkmap(tmp_path / "controle-Rooster_Her.xlsx")["Rooster_Her"]) == 3


def test_origineel_wordt_niet_overschreven(tmp_path, monkeypatch):
    bron = tmp_path / "werkmap.xlsx"
    mv.schrijf(bron)
    app = roosterapp.QApplication.instance() or roosterapp.QApplication([])  # noqa: F841
    v = roosterapp.Venster()
    v.open(str(bron))
    v.maak()
    voor = bron.read_bytes()
    monkeypatch.setattr(roosterapp.QMessageBox, "warning", lambda *a: None)
    assert v.opslaan(str(bron)) is None and bron.read_bytes() == voor


def test_fouten_blokkeren_opslaan(tmp_path):
    b = mv.voorbeeld_bladen()
    b["Slots_Kans1"][2][1] = "??"
    from openpyxl import Workbook
    wb = Workbook(); wb.remove(wb.active); rc.schrijf_bladen(wb, b); wb.save(tmp_path / "k.xlsx")
    app = roosterapp.QApplication.instance() or roosterapp.QApplication([])  # noqa: F841
    v = roosterapp.Venster()
    v.open(str(tmp_path / "k.xlsx"))
    r = v.maak()
    assert r["fouten"] and not v.knop_opslaan.isEnabled() and v.tabs.currentWidget() is v.tabel_meldingen


def test_wijziging_na_maken_vraagt_opnieuw_maken(tmp_path):
    bron = tmp_path / "werkmap.xlsx"
    mv.schrijf(bron)
    app = roosterapp.QApplication.instance() or roosterapp.QApplication([])  # noqa: F841
    v = roosterapp.Venster()
    v.open(str(bron))
    v.maak()
    assert v.knop_pdf.isEnabled()
    v.modus_groep.buttons()[1].setChecked(True)
    assert not v.knop_pdf.isEnabled() and not v.knop_opslaan.isEnabled()
    assert v.maak()["modus"] == "her" and v.knop_pdf.isEnabled()


def test_instellingen_formulier_heen_en_terug():
    app = roosterapp.QApplication.instance() or roosterapp.QApplication([])  # noqa: F841
    v = roosterapp.Venster()
    assert v.instellingen.waarden() == rc.STANDAARD
    anders = {**rc.STANDAARD, "jaar": 2, "duur2": 20, "pauze_van": 0.5, "pauze_tot": 0.5 + 30 / 1440,
              "ttv_eerst": "Nee", "her_beo": "Verplicht", "blad_meldingen": "Log"}
    v.instellingen.zet(anders)
    assert v.instellingen.waarden() == anders
    v.instellingen.herstel()
    assert v.instellingen.waarden() == rc.STANDAARD


def test_instellingen_komen_in_rooster_en_werkmap(tmp_path):
    bron = tmp_path / "werkmap.xlsx"
    mv.schrijf(bron)
    app = roosterapp.QApplication.instance() or roosterapp.QApplication([])  # noqa: F841
    v = roosterapp.Venster()
    v.open(str(bron))
    assert v.instellingen.pauze.isChecked()  # pauze uit de werkmap overgenomen
    v.instellingen.velden["duur1"].setValue(20)
    v.instellingen.velden["blad_rooster1"].setText("Rooster docenten")
    r = v.maak()
    assert "toets 20 min" in r["meldingen"][0][1] and r["namen"]["rooster"] == "Rooster docenten"
    doel = v.opslaan(str(tmp_path / "uit.xlsx"))
    uit = rc.lees_werkmap(doel)
    assert "Rooster docenten" in uit and rc.instellingen_waarden(uit["Instellingen"])["duur1"] == 20
