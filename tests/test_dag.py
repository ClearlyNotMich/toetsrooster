"""Werkwijze met blad Toetsdag, nagebouwd naar een echte toetsdag (verzonnen namen)."""
from collections import Counter

import maak_voorbeeld as mv
import rooster_core as rc


def plan(modus="kans1", wijzig=None):
    b = mv.dag_bladen()
    if wijzig:
        wijzig(b)
    return rc.maak_rooster(b, modus)


def rijen(r, blad="Rooster_Kans1"):
    kop, *data = r["bladen"][blad]
    return [dict(zip(kop, x)) for x in data]


def tijd(x):
    return rc.tijd_tekst(round(x * 1440))


def met(**w):
    def wijzig(b):
        b["Instellingen"] = rc.instellingen_matrix({**rc.instellingen_waarden(b["Instellingen"]), **w})
    return wijzig


# ---------------------------------------------------------------- inlezen

def test_pauzes_lezen():
    assert rc.lees_pauzes("11:15-11:40, 13.00 – 13.55;15:15-15:40") == [[675, 700], [780, 835], [915, 940]]
    assert rc.lees_pauzes("") == [] and rc.lees_pauzes("13:00-12:00") is None
    assert rc.lees_pauzes("11:00-12:00, 11:30-12:30") is None and rc.lees_pauzes("lunch") is None
    assert rc.lees_pauzes("13:00-13:30, 11:00-11:15") == [[660, 675], [780, 810]]


def test_tijdgrid_zoals_echte_toetsdag():
    s = rc.lees_instellingen(None, [])
    assert [rc.tijd_tekst(t) for t in rc.tijdgrid(s)] == [
        "09:40", "10:00", "10:20", "10:40", "11:00", "11:45", "12:05", "12:25", "12:45",
        "14:00", "14:20", "14:40", "15:00", "15:45", "16:05", "16:25", "16:45"]


def test_kolommen_op_begin_van_kopnaam_en_slash():
    kop = ["Studentnummer", "Roepnaam", "Klas p2", "Niet inroosteren bij SB-docent P2"]
    assert (rc.kolom(kop, "voornaam", "roepnaam"), rc.kolom(kop, "klas"), rc.kolom(kop, "nietinroosterenbijsbdocent")) == (1, 2, 3)
    assert rc.namen_lijst("Sofie/Youri; Ann ,Bram") == ["Sofie", "Youri", "Ann", "Bram"]


def test_voorkeur_en_opmerkingen():
    assert rc.voorkeur_in("liever in de ochtend") == "Ochtend" and rc.voorkeur_in("plaatsen") == ""
    assert rc.heeft_woord("ttv nodig", "ttv") and not rc.heeft_woord("attvx", "ttv")
    meld = []
    b = mv.dag_bladen()
    st, _ = rc.lees_studenten(b["Studenten"], "Studenten", [], meld)
    assert st[0]["ttv"] and st[1]["voorkeur"] == "Ochtend" and st[30]["voorkeur"] == "Middag"
    assert st[44]["verboden"] == ["Bram", "Eef", "Gijs Goud"] and st[0]["klas"] == "P2A"
    assert sum("Opmerking bij" in m[1] for m in meld) == 3


def test_ongeldige_pauzes_en_tijden_geven_fouten():
    r = plan(wijzig=met(pauzes="lunch", start="25:00", eind="08:00"))
    assert len(r["fouten"]) == 3 and set(r["bladen"]) == {"Meldingen"}  # ongeldige start valt terug op 09:40 > 08:00
    r = plan(wijzig=met(start="17:00", eind="09:00"))
    assert any("vóór" in f for f in r["fouten"])


# ---------------------------------------------------------------- toetsdag

def test_echte_dagstructuur():
    r = plan()
    alle = rijen(r)
    studenten = [x for x in alle if x["bijzheden"] != rc.VRIJ]
    assert r["fouten"] == [] and len(studenten) == 61 and not any(x["bijzheden"] == rc.NIET for x in alle)
    assert sum(x["bijzheden"] == rc.VRIJ for x in alle) == 24 and len(alle) == 85
    # uitsluitingen gerespecteerd
    verboden = {"P2A": set(), "P2B": {"Ann", "Bram"}, "P2C": {"Bram", "Eef"}}
    assert not [x for x in studenten if x["Beoordelaar"] in verboden[x["klas"]]]
    # TTV vlak voor een pauze, ochtendwens in het eerste slot
    ttv = next(x for x in studenten if x["bijzheden"].startswith("TTV"))
    assert tijd(ttv["Tijd"]) in ("11:00", "12:45", "15:00") and round((ttv["Eindtijd"] - ttv["Tijd"]) * 1440) == 20
    bas = next(x for x in studenten if "ochtend" in x["bijzheden"])
    assert tijd(bas["Tijd"]) == "09:40"
    assert "ochtend" in bas["bijzheden"]  # volledige opmerking in bijzonderheden
    # beoordelaarswissel om 12:25
    c139 = [x for x in alle if x["Lokaal"] == "C1.39"]
    assert {x["Beoordelaar"] for x in c139 if x["Tijd"] * 1440 < 745} == {"Eef"}
    assert {x["Beoordelaar"] for x in c139 if x["Tijd"] * 1440 >= 745} == {"Fien"}


def test_simus_rouleren_per_blok():
    alle = rijen(plan())
    simus = ["Siem", "Tom", "Uma", "Vera", "Wout"]
    lokalen = ["C1.33-1", "C1.33-2", "C1.23-1", "C1.23-2", "C1.39"]
    grens = [700, 835, 940]
    for x in alle:
        blok = sum(1 for g in grens if x["Tijd"] * 1440 >= g)
        assert x["simucliënt"] == simus[(lokalen.index(x["Lokaal"]) + blok) % 5], (x["Lokaal"], tijd(x["Tijd"]))
    r = plan(wijzig=met(simu_rotatie="Nee"))
    assert {(x["Lokaal"], x["simucliënt"]) for x in rijen(r)} == set(zip(lokalen, simus))


def test_simu_vanaf_tot_en_te_weinig():
    def wim_ochtend(b):
        b["Simu"][5][3] = "12:00"
    r = plan(wijzig=wim_ochtend)
    wim = [x for x in rijen(r) if x["simucliënt"] == "Wout"]
    assert wim and all(round(x["Eindtijd"] * 1440) <= 720 for x in wim)  # per slot binnen Vanaf/Tot
    assert any(tijd(x["Tijd"]) == "11:45" for x in wim)  # 11:45-12:00 past nog
    assert sum("4 simucliënt(en) beschikbaar voor 5 lokalen" in m[1] for m in r["meldingen"]) == 2  # middagblokken


def test_simus_later_dan_eerste_toets_dubbel_en_andere_datum():
    """Zoals een echte invoerfout: simu's vanaf 10:00 terwijl de eerste toets 09:40 is, en twee namen dubbel."""
    def invoer(b):
        b["Simu"] = [b["Simu"][0]] + [[mv.TOETS, n, "10:00", "17:00"] for n in ("Siem", "Tom", "Uma", "Vera", "Wout", "Siem")]
    r = plan(wijzig=invoer)
    alle = rijen(r)
    assert not [x for x in alle if tijd(x["Tijd"]) == "09:40"]  # om 09:40 is nog geen simu
    assert {tijd(x["Tijd"]) for x in alle if x["Lokaal"] == "C1.39"} >= {"10:00", "11:00", "11:45"}
    assert any("Siem staat al eerder op 14-04-2026" in m[1] for m in r["meldingen"])
    assert any("5 slot(s) zonder beschikbare simucliënt" in m[1] for m in r["meldingen"])
    assert sum(x["bijzheden"] != rc.VRIJ for x in alle) == 61
    r = plan("her", invoer)  # herkansing op 27-05: geen simu's die dag
    assert any("Geen simucliënten voor 27-05-2026" in m[1] and "14-04-2026" in m[1] for m in r["meldingen"])


def test_meerdere_pauzes_en_casus_na_pauze():
    def na(b):
        for rij in b["Toetsdag_Kans1"][1:]:
            rij[3] = rij[2] + "b"
    for regel, verwacht in (("Na pauze 2", [False, False, True, True]), ("Na elke pauze afwisselen", [False, True, False, True]),
                            ("Nee", [False] * 4)):
        r = plan(wijzig=lambda b: (na(b), met(casus_na=regel)(b)))
        per_blok = {}
        for x in rijen(r):
            per_blok.setdefault(sum(1 for g in (700, 835, 940) if x["Tijd"] * 1440 >= g), set()).add(x["Casus"].endswith("b"))
        assert [per_blok[i] == {True} for i in range(4)] == verwacht, regel
    for x in rijen(plan()):  # geen gewone toets overlapt een pauze
        a, b = round(x["Tijd"] * 1440), round(x["Eindtijd"] * 1440)
        if not x["bijzheden"].startswith("TTV"):
            assert not any(a < q and b > p for p, q in ((675, 700), (780, 835), (915, 940)))


def test_vrije_plekken_uit_en_niet_op_uitdraai():
    r = plan()
    assert len(r["bladen"]["Uitdraai_Kans1"]) == 62
    r = plan(wijzig=met(vrije_plekken="Nee"))
    assert len(rijen(r)) == 61


def test_herkansing_op_toetsdag():
    r = plan("her")
    stud = {x["Voornaam"]: x for x in rijen(r, "Rooster_Her") if x["Voornaam"]}
    assert stud["Mila"]["Beoordelaar"] != "Ann" and stud["Otto"]["Beoordelaar"] != "Bram"
    assert stud["Otto"]["bijzheden"].startswith("TTV")


def test_voorkeur_niet_gehaald_geeft_waarschuwing():
    def vol(b):
        b["Toetsdag_Kans1"] = b["Toetsdag_Kans1"][:2]  # één lokaal: niet iedereen past
        b["Studenten"][31][7] = "Ochtend"
    r = plan(wijzig=vol)
    assert any(x["bijzheden"] == rc.NIET for x in rijen(r))


def test_toetsdag_fouten():
    def kapot(b):
        b["Toetsdag_Kans1"][1][6] = "Fien"  # Beoordelaar 2 zonder Wissel om
        b["Toetsdag_Kans1"][5][1] = "C1.33-2"  # dubbel lokaal
        b["Toetsdag_Kans1"][3][5] = ""  # geen beoordelaar
    r = plan(wijzig=kapot)
    assert len(r["fouten"]) == 3


def test_oude_bladen_blijven_werken_als_toetsdag_leeg_is():
    b = mv.voorbeeld_bladen()
    b["Toetsdag_Kans1"] = [["Datum", "Lokaal", "Beoordelaar"]]
    r = rc.maak_rooster(b, "kans1")
    assert r["fouten"] == [] and len(rijen(r)) == 12
    del b["Slots_Kans1"]
    r = rc.maak_rooster(b, "kans1")  # geen oude slots meer: dan telt de (lege) toetsdag
    assert r["fouten"] == [] and len(rijen(r)) == 12 and all(x["bijzheden"] == rc.NIET for x in rijen(r))


def test_datumnotaties():
    goed = ["14-04-2026", "14-4-26", "2026-04-14", "2026/4/14", "14.04.2026", "14/04/2026", "14 april 2026",
            "di 14 april 2026", "Dinsdag 14 april 2026", "14 apr. 2026", "14-04-2026 00:00", "2026-04-14 00:00:00",
            "2026-04-14T00:00:00", "April 14, 2026", "14 Apr 26", "46126", 46126, 46126.5]
    assert {g if rc.naar_datum(g) != 46126 else "ok" for g in goed} == {"ok"}
    assert rc.naar_datum("3 mrt 2026") == rc.naar_datum("3 maart 2026") == rc.naar_datum("March 3, 2026") == 46084
    for fout in ["14-4", "14 april", "31-02-2026", "1 foo 2026", "", "morgen", 0]:
        assert rc.naar_datum(fout) is None, fout


def test_datum_als_tekst_in_toetsdag_en_simu():
    def tekst(b):
        for rij, d in zip(b["Toetsdag_Kans1"][1:], ["14-4-26", "di 14 april 2026", "2026-04-14", "14/04/2026", "14 apr. 26"]):
            rij[0] = d
        for rij in b["Simu"][1:6]:
            rij[0] = "dinsdag 14 april 2026"
    r = plan(wijzig=tekst)
    assert r["fouten"] == [] and sum(x["bijzheden"] != rc.VRIJ for x in rijen(r)) == 61

    def zonder_jaar(b):
        b["Toetsdag_Kans1"][1][0] = "14 april"
    r = plan(wijzig=zonder_jaar)
    assert len(r["fouten"]) == 1 and "'14 april'" in r["fouten"][0] and "14 april 2026" in r["fouten"][0]


# ---------------------------------------------------------------- conceptblad (lijstvorm)

def concept(wijzig=None, modus="kans1"):
    b = mv.concept_bladen()
    if wijzig:
        wijzig(b)
    return rc.maak_rooster(b, modus)


def test_concept_zoals_roostermaker_het_opschrijft():
    r = concept()
    assert r["fouten"] == []
    alle = rijen(r)
    studenten = [x for x in alle if x["bijzheden"] != rc.VRIJ]
    assert len(studenten) == 61 and not any(x["bijzheden"] == rc.NIET for x in alle)
    assert {tijd(x["Tijd"]) for x in alle} == {"10:00", "10:20", "10:40", "11:00", "11:45", "12:05", "12:25", "12:45",
                                               "14:00", "14:20", "14:40", "15:00", "15:45", "16:05", "16:25", "16:45"}
    per_lokaal = {x["Lokaal"]: (x["Casus"], x["Beoordelaar"]) for x in alle if x["Tijd"] * 1440 < 700}
    assert per_lokaal["A1"] == ("K1 man", "Ann") and per_lokaal["C2"] == ("K7 vrouw", "Fien")
    assert {x["Beoordelaar"] for x in alle if x["Lokaal"] == "C2" and x["Tijd"] * 1440 >= 810} == {"Hans"}
    assert not [x for x in alle if x["Lokaal"] == "C2" and x["Beoordelaar"] == "Fien" and x["Eindtijd"] * 1440 > 780]
    assert "Zeger" not in {x["simucliënt"] for x in alle}  # 7 nodig, de 8e is reserve
    tekst = " ".join(m[1] for m in r["meldingen"])
    for stuk in ("staat dubbel", "Niet ingedeeld (reserve): Ida (reactie nog afwachten)", "reserve: Zeger",
                 "C2 Fien (tot 13:00) → Hans (vanaf 13:30)", "7 lokalen, 16 tijden (10:00-17:00), toets 15 min, 3 pauze(s)"):
        assert stuk in tekst, stuk


def test_concept_gaat_voor_toetsdag_met_waarschuwing():
    def ook_toetsdag(b):
        b["Toetsdag_Kans1"] = mv.dag_bladen()["Toetsdag_Kans1"]
    r = concept(ook_toetsdag)
    assert any("wordt niet gebruikt: het conceptblad 'Concept' gaat voor" in m[1] for m in r["meldingen"])
    assert {x["Lokaal"] for x in rijen(r)} == {"A1", "A2", "B1", "B2", "C1", "Praktijkhuis", "C2"}


def test_concept_reserve_inzetten_en_studenten_uit_concept():
    def krap(b):
        rijen_ = b["Concept"]
        start = [i for i, r in enumerate(rijen_) if r[0] == "inzet"][0]
        del rijen_[start + 1:start + 3]  # Bram en Cor weg -> te weinig beoordelaars
        del b["Studenten"]
        i = [k for k, r in enumerate(rijen_) if r[0] == "studenten"][0]
        rijen_[i][1] = "Lieve van der Bloemhof"
        rijen_.insert(i + 1, ["", "Pim Vos"])
    r = concept(krap)
    tekst = " ".join(m[1] for m in r["meldingen"])
    assert "Reserve Ida ingezet" in tekst and "Reserve Jet ingezet" in tekst
    assert "Studenten uit blad 'Concept' (2)" in tekst
    stud = {(x["Voornaam"], x["vv"], x["Achternaam"]) for x in rijen(r) if x["Voornaam"]}
    assert stud == {("Lieve", "van der", "Bloemhof"), ("Pim", "", "Vos")}
    assert r["bladen"]["Studenten"][0][:4] == ["Studentnummer", "Voornaam", "Tussenvoegsel", "Achternaam"]


def test_concept_fouten():
    def kapot(b):
        b["Concept"][1][1] = "15 december"  # geen jaartal
        i = [k for k, r in enumerate(b["Concept"]) if r[0] == "tijden"][0]
        b["Concept"][i][1] = "tien uur"
    r = concept(kapot)
    assert len(r["fouten"]) == 2 and any("datum" in f for f in r["fouten"]) and any("tien uur" in f for f in r["fouten"])


def test_simus_wisselen_na_elke_toets():
    def per_toets(b):
        b["Instellingen"] = rc.instellingen_matrix({"simu_rotatie": "Na elke toets"})
    alle = rijen(concept(per_toets))
    a1 = [x["simucliënt"] for x in sorted(alle, key=lambda x: x["Tijd"]) if x["Lokaal"] == "A1"]
    assert a1[:8] == ["Siem", "Tom", "Uma", "Vera", "Wout", "Xan", "Yara", "Siem"]
    for t in {x["Tijd"] for x in alle}:  # nooit twee lokalen tegelijk met dezelfde simu
        simus = [x["simucliënt"] for x in alle if x["Tijd"] == t]
        assert len(simus) == len(set(simus))
    assert rc.lees_instellingen(rc.instellingen_matrix({"simu_rotatie": "Ja"}), [])["simu_rotatie"] == "Na elke pauze"
