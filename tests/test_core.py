"""Gedrag van de roosterlogica op verzonnen gegevens (tools/maak_voorbeeld.py)."""
import copy

import maak_voorbeeld as mv
import rooster_core as rc


def plan(modus="kans1", wijzig=None):
    b = mv.voorbeeld_bladen()
    if wijzig:
        wijzig(b)
    return rc.maak_rooster(b, modus), b


def rijen(r, blad):
    kop, *data = r["bladen"][blad]
    return [dict(zip(kop, x)) for x in data]


def test_iedereen_ingeroosterd_en_geen_dubbele_boekingen():
    r, _ = plan()
    rooster = rijen(r, "Rooster_Kans1")
    assert len(rooster) == 12 and all(x["bijzheden"] != "NIET INGEROOSTERD" for x in rooster)
    for soort in ("Lokaal", "Beoordelaar", "simucliënt"):
        per = {}
        for x in rooster:
            per.setdefault((x["Datum"], x[soort]), []).append((x["Tijd"], x["Eindtijd"]))
        for blokken in per.values():
            blokken.sort()
            assert all(a[1] <= b[0] + 1e-9 for a, b in zip(blokken, blokken[1:])), soort


def test_toetsduur_en_ttv_aan_einde_blok_voor_pauze():
    r, _ = plan()
    for x in rijen(r, "Rooster_Kans1"):
        duur = round((x["Eindtijd"] - x["Tijd"]) * 1440)
        if x["bijzheden"].startswith("TTV"):
            assert duur == 15 and rc.tijd_tekst(round(x["Tijd"] * 1440)) == "10:50"  # laatste slot vóór de pauze (11:00-11:30)
        else:
            assert duur == 10 and (x["Eindtijd"] * 1440 <= 660 + 1e-6 or x["Tijd"] * 1440 >= 690 - 1e-6)


def test_casus_wisselt_na_pauze():
    r, _ = plan()
    tijden = [x["Tijd"] * 1440 for x in rijen(r, "Rooster_Kans1")]
    assert min(tijden) < 660 and max(tijden) >= 690  # er zijn studenten vóór én na de pauze
    for x in rijen(r, "Rooster_Kans1"):
        na = x["Tijd"] * 1440 >= 690 - 1e-6
        assert x["Casus"] == {"A": ("XY", "BB"), "B": ("MM", "NN")}[x["Lokaal"]][na]


def test_jaar2_duur_instelbaar():
    def jaar2(b):
        b["Instellingen"] = rc.instellingen_matrix({"Jaar": 2, "Toetsduur jaar 2 (min)": 20, "TTV-toetsduur jaar 2 (min)": 40})
    r, _ = plan(wijzig=jaar2)
    duren = {round((x["Eindtijd"] - x["Tijd"]) * 1440) for x in rijen(r, "Rooster_Kans1")}
    assert duren == {20, 40}


def test_beperkingen_beoordelaar():
    r, _ = plan()
    per = {x["Voornaam"]: x["Beoordelaar"] for x in rijen(r, "Rooster_Kans1")}
    assert per["Bas"] != "Ann" and per["Daan"] != "Bram" and per["Fleur"] not in ("Ann", "Cor")


def test_uitdraai_alleen_naam_lokaal_tijd():
    r, _ = plan()
    kop, *data = r["bladen"]["Uitdraai_Kans1"]
    assert kop == ["Naam", "Lokaal", "Tijd"] and len(data) == 12
    cellen = {str(c) for rij in data for c in rij}
    assert not cellen & {"XY", "MM", "BB", "NN", "Ann", "Bram", "Cor", "Sanne", "Tom", "Uma", "Gesprek"}
    assert not any("9000" in c for c in cellen)
    verwacht = {(" ".join(x for x in (r["Voornaam"], r["vv"], r["Achternaam"]) if x), r["Lokaal"],
                 f"{rc.datum_tekst(r['Datum'])} {rc.tijd_tekst(round(r['Tijd'] * 1440))}") for r in rijen(r, "Rooster_Kans1")}
    assert {tuple(x) for x in data} == verwacht


def test_eerste_kans_schrijft_juiste_kolommen():
    r, _ = plan()
    kop, *data = r["bladen"]["Studenten"]
    i = kop.index
    anna = data[0]
    assert anna[i("TTV")] == "Nee" and anna[i("IsHerkanser")] == "Nee"  # niet overschreven (oude fout)
    assert anna[i("EersteDatum")] == 46128 and anna[i("EersteBeoordelaar")] == "Ann" and anna[i("EersteCasus")] == "XY"
    mila = data[12]
    assert mila[i("EersteBeoordelaar")] == "Ann"  # herkanser: eerste-kansgegevens blijven staan


def test_herkansing_andere_beoordelaar_en_casus():
    r, _ = plan("her")
    per = {x["Voornaam"]: x for x in rijen(r, "Rooster_Her")}
    assert set(per) == {"Mila", "Noah"}
    assert per["Mila"]["Beoordelaar"] != "Ann" and per["Mila"]["Casus"] != "XY"
    assert per["Noah"]["Beoordelaar"] != "Bram" and per["Noah"]["Casus"] != "MM"
    assert "Studenten" not in r["bladen"]


def test_herkansing_valt_terug_met_melding():
    def alleen_ann(b):
        b["Beoordelaars"] = [b["Beoordelaars"][0]] + [x for x in b["Beoordelaars"][1:] if x[2] == "Ann"]
    r, _ = plan("her", alleen_ann)
    mila = next(x for x in rijen(r, "Rooster_Her") if x["Voornaam"] == "Mila")
    assert "Zelfde beoordelaar als 1e kans" in mila["bijzheden"]
    assert any("zelfde beoordelaar" in m[1] for m in r["bladen"]["Meldingen"])


def test_niet_ingeroosterd_wordt_getoond():
    def weinig_slots(b):
        b["Slots_Kans1"] = b["Slots_Kans1"][:4]
    r, _ = plan(wijzig=weinig_slots)
    rooster = rijen(r, "Rooster_Kans1")
    assert len(rooster) == 12 and sum(x["bijzheden"] == "NIET INGEROOSTERD" for x in rooster) >= 8
    assert any("NIET ingeroosterd" in m[1] for m in r["bladen"]["Meldingen"])


def test_fout_laat_rooster_ongemoeid():
    def kapot(b):
        b["Slots_Kans1"][3][1] = "kwart over"
        b["Studenten"][0][1] = "Naam"
    r, _ = plan(wijzig=kapot)
    assert set(r["bladen"]) == {"Meldingen"} and len(r["fouten"]) == 2


def test_oude_scriptfout_in_isherkanser_geeft_waarschuwing():
    def oud(b):
        b["Studenten"][1][8] = 46128
    r, _ = plan(wijzig=oud)
    assert any("rij 2" in m[1] and "IsHerkanser" in m[1] for m in r["bladen"]["Meldingen"])
    assert len(rijen(r, "Rooster_Kans1")) == 12


def test_ontbrekende_instellingen_worden_aangemaakt():
    def zonder(b):
        del b["Instellingen"]
    r, _ = plan(wijzig=zonder)
    assert r["bladen"]["Instellingen"] == rc.instellingen_matrix()
    assert "geen pauze" in r["bladen"]["Meldingen"][1][1]


def test_tijden_als_tekst():
    assert rc.naar_minuten("9:05") == 545 and rc.naar_minuten(0.375) == 540 and rc.naar_datum("16-04-2026") == 46128
    assert rc.naar_minuten("25:00") is None and rc.naar_datum("31-02-2026") is None
