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
    assert rc.namen_lijst("Floor/Huub; Ann ,Bram") == ["Floor", "Huub", "Ann", "Bram"]


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


def test_simu_vast_lokaal_per_simu():
    def vast(b):
        b["Instellingen"] = rc.instellingen_matrix({"simu_rotatie": "Na elke toets"})
        b["Simu"][0].append("Vast lokaal")
        for rij in b["Simu"][1:]:
            rij.append("")
        b["Simu"][1][4] = "C2"   # Siem altijd in C2
        b["Simu"][2][4] = "Ja"   # Tom in het eerste vrije lokaal (A1)
        b["Simu"][3][4] = "Nee"  # Uma wisselt (zoals leeg)
    r = concept(vast)
    alle = rijen(r)
    assert {x["Lokaal"] for x in alle if x["simucliënt"] == "Siem"} == {"C2"}
    assert {x["Lokaal"] for x in alle if x["simucliënt"] == "Tom"} == {"A1"}
    assert {x["simucliënt"] for x in alle if x["Lokaal"] == "C2"} == {"Siem"}
    wisselend = {x["simucliënt"] for x in alle if x["Lokaal"] == "B1"}
    assert len(wisselend) > 1 and not wisselend & {"Siem", "Tom"}  # de rest wisselt na elke toets
    for t in {x["Tijd"] for x in alle}:
        simus = [x["simucliënt"] for x in alle if x["Tijd"] == t]
        assert len(simus) == len(set(simus))


def test_simu_vast_lokaal_fouten_en_zonder_wissel_instelling():
    def vast(b):
        b["Simu"][0].append("Vast lokaal")
        for rij in b["Simu"][1:]:
            rij.append("")
        b["Simu"][1][4] = "Z9"   # bestaat niet
        b["Simu"][2][4] = "A1"
        b["Simu"][3][4] = "A1"   # al bezet
    r = concept(vast)
    tekst = " ".join(m[1] for m in r["meldingen"])
    assert "Siem: vast lokaal 'Z9' bestaat niet" in tekst and "Uma: lokaal A1 is al vast voor Tom" in tekst
    assert {x["simucliënt"] for x in rijen(r) if x["Lokaal"] == "A1"} == {"Tom"}


# ---------------------------------------------------------------- kenmerken (keuken) en 'Kan spelen'

def test_kenmerken_en_koppelen():
    assert rc.kenmerken("C1.36 (keuken)") == ("C1.36", ["keuken"])
    assert rc.kenmerken("K3 vrouw (keuken, rolstoel)") == ("K3 vrouw", ["keuken", "rolstoel"])
    assert rc.kenmerken("A1") == ("A1", [])
    kamers = [("A1", []), ("A2", ["keuken"]), ("B1", []), ("B2", ["keuken"])]
    # casus 0 en 1 willen een keuken, 2 en 3 niet: keukencasussen naar A2/B2, de rest vult op volgorde
    assert rc.koppel_lokalen(kamers, [["keuken"], ["keuken"], [], []]) == [1, 3, 2, 0]
    assert rc.koppel_lokalen(kamers, [[], ["keuken"], [], []]) == [0, 1, 2, 3]  # staat al goed: niets verschuift
    assert rc.koppel_lokalen(kamers, [["keuken"]] * 3 + [[]])[2] in (0, 2)  # derde keukencasus past niet meer
    assert rc.speelt(["vrouw"], "P3 vrouw") and not rc.speelt(["vrouw"], "P1 man") and rc.speelt([], "P1 man")
    assert rc.speelt(["P1", "P2"], "P2 man") and not rc.speelt(["P1"], "P10 man") and not rc.speelt(["man"], "P3 vrouw")


def met_keuken(b):
    blad = b["Concept"]
    lok = [i for i, r in enumerate(blad) if r[0] == "lokalen"][0]
    cas = [i for i, r in enumerate(blad) if r[0] == "casussen"][0]
    blad[lok + 3][1] = "B2 (keuken)"   # 4e lokaal
    blad[lok + 5][1] = "Praktijkhuis (keuken)"
    blad[cas][1] = "K1 man (keuken)"   # 1e casus (Ann) wil een keuken
    blad[cas + 6][1] = "K7 vrouw (keuken)"  # 7e casus (Fien/Hans) ook


def test_concept_casus_naar_keuken():
    r = concept(met_keuken)
    assert r["fouten"] == []
    alle = rijen(r)
    per_casus = {x["Casus"]: (x["Lokaal"], x["Beoordelaar"]) for x in alle if x["Tijd"] * 1440 < 700}
    assert per_casus["K1 man"] == ("B2", "Ann")  # beoordelaar verhuist mee met de casus
    assert per_casus["K7 vrouw"][0] == "Praktijkhuis" and per_casus["K7 vrouw"][1] == "Fien"
    assert all("(" not in x["Lokaal"] and "(" not in x["Casus"] for x in alle)  # kenmerken niet in het rooster
    assert any("Casus K1 man staat in lokaal B2 (keuken) in plaats van A1" in m[1] for m in r["meldingen"])
    assert sum(x["bijzheden"] != rc.VRIJ for x in alle) == 61


def test_te_weinig_keukens_geeft_waarschuwing():
    def drie(b):
        met_keuken(b)
        cas = [i for i, r in enumerate(b["Concept"]) if r[0] == "casussen"][0]
        b["Concept"][cas + 2][1] = "K3 vrouw (keuken)"
    r = concept(drie)
    tekst = " ".join(m[1] for m in r["meldingen"])
    assert tekst.count("vraagt keuken, maar op 15-12-2026 is daar geen vrij lokaal voor") == 1  # 3 keukencasussen, 2 keukens
    keuken = {x["Casus"] for x in rijen(r) if x["Lokaal"] in ("B2", "Praktijkhuis")}
    assert len(keuken) == 2 and keuken <= {"K1 man", "K3 vrouw", "K7 vrouw"}


def test_toetsdag_blad_met_keuken():
    def keuken(b):
        b["Toetsdag_Kans1"][5][1] = "C1.39 (keuken)"
        b["Toetsdag_Kans1"][1][2] = "Q 1 (keuken)"
    r = plan(wijzig=keuken)
    per = {x["Casus"]: (x["Lokaal"], x["Beoordelaar"]) for x in rijen(r) if x["Tijd"] * 1440 < 700}
    assert per["Q 1"] == ("C1.39", "Ann") and per["I 1"][0] == "C1.33-1"


def test_simu_kan_spelen():
    def gender(b):
        b["Instellingen"] = rc.instellingen_matrix({"simu_rotatie": "Na elke toets"})
        b["Simu"][0] += ["Vast lokaal", "Kan spelen"]
        kan = ["man", "man", "vrouw", "vrouw", "vrouw", "vrouw", "man", ""]
        for rij, k in zip(b["Simu"][1:], kan):
            rij += ["", k]
    r = concept(gender)
    alle = rijen(r)
    simu_kan = dict(zip(["Siem", "Tom", "Uma", "Vera", "Wout", "Xan", "Yara"], ["man", "man", "vrouw", "vrouw", "vrouw", "vrouw", "man"]))
    for x in alle:
        assert simu_kan[x["simucliënt"]] in x["Casus"], (x["simucliënt"], x["Casus"])
    assert sum(x["bijzheden"] != rc.VRIJ for x in alle) == 61
    assert len({x["simucliënt"] for x in alle if x["Lokaal"] == "A1"}) > 1  # wisselt nog steeds, binnen 'man'


def test_casus_zonder_passende_simu():
    def niemand(b):
        b["Simu"][0].append("Kan spelen")
        for rij in b["Simu"][1:]:
            rij.append("man")
    r = concept(niemand)
    tekst = " ".join(m[1] for m in r["meldingen"])
    assert "Casus K3 vrouw op 15-12-2026: geen simucliënt die deze casus kan spelen" in tekst
    assert not [x for x in rijen(r) if "vrouw" in x["Casus"] and x["bijzheden"] != rc.VRIJ]


# ---------------------------------------------------------------- beoordelaars met tijden, ruilen, lokaal zonder iemand

def test_lees_inzet_tijden():
    for t, verwacht in [("Fien tot 13.00", ("Fien", None, 780)), ("Hans vanaf 13.30", ("Hans", 810, None)),
                        ("Dorus 10.00-12.00", ("Dorus", 600, 720)), ("Dorus van 10.00 tot 12.00", ("Dorus", 600, 720)),
                        ("Ida van Berkel", ("Ida van Berkel", None, None)), ("Bodil ochtend", ("Bodil", None, 720))]:
        x = rc.lees_inzet(t, 720)
        assert (x["naam"], x["van"], x["tot"]) == verwacht, t


def dag_met(*rijen_):
    def wijzig(b):
        kop = b["Toetsdag_Kans1"][0] + ["Beoordelaar 3"]
        b["Toetsdag_Kans1"] = [kop] + [list(r) + [""] * (len(kop) - len(r)) for r in rijen_]
    return wijzig


def test_beoordelaars_met_tijden_en_derde_beoordelaar():
    T = mv.TOETS
    r = plan(wijzig=dag_met(
        [T, "A", "Q 1", "", "COPM", "Ann tot 11.15", "Bram 11.45-13.00", "", "Cor vanaf 14.00"],
        [T, "B", "R 1", "", "COPM", "Dirk", "", "", ""],
        [T, "C", "R 2", "", "COPM", "Eef", "Fien", "13.00", ""],
    ))
    assert r["fouten"] == []
    a = {tijd(x["Tijd"]): x["Beoordelaar"] for x in rijen(r) if x["Lokaal"] == "A"}
    assert a["09:40"] == a["11:00"] == "Ann" and a["11:45"] == a["12:45"] == "Bram" and a["14:00"] == a["16:45"] == "Cor"
    c = {tijd(x["Tijd"]): x["Beoordelaar"] for x in rijen(r) if x["Lokaal"] == "C"}
    assert c["12:45"] == "Eef" and c["14:00"] == "Fien"


def test_beoordelaars_ruilen_van_lokaal():
    T = mv.TOETS
    r = plan(wijzig=dag_met(
        [T, "A", "Q 1", "", "COPM", "Ann tot 13.00", "Bram vanaf 13.00", "", ""],
        [T, "B", "R 1", "", "COPM", "Bram tot 13.00", "Ann vanaf 13.00", "", ""],
    ))
    assert r["fouten"] == [] and not any("twee lokalen" in m[1] for m in r["meldingen"])
    a = {x["Beoordelaar"] for x in rijen(r) if x["Lokaal"] == "A" and x["Tijd"] * 1440 >= 780}
    assert a == {"Bram"} and {x["Casus"] for x in rijen(r) if x["Beoordelaar"] == "Ann"} == {"Q 1", "R 1"}


def test_beoordelaar_dubbel_ingezet_en_fouten():
    T = mv.TOETS
    r = plan(wijzig=dag_met(
        [T, "A", "Q 1", "", "COPM", "Ann", "", "", ""],
        [T, "B", "R 1", "", "COPM", "Bram tot 12.00", "Ann vanaf 11.00", "", ""],
    ))
    assert any("Ann staat op 14-04-2026 van 11:00 tot 17:00 in twee lokalen (A en B)" in m[1] for m in r["meldingen"])
    r = plan(wijzig=dag_met([T, "A", "Q 1", "", "COPM", "Ann", "Bram", "", ""]))
    assert any("vul 'Wissel om' in, of zet tijden in de cel" in f for f in r["fouten"])
    r = plan(wijzig=dag_met([T, "A", "Q 1", "", "COPM", "Ann", "", "13.00", ""]))
    assert any("vraagt ook een 'Beoordelaar 2'" in f for f in r["fouten"])


def zeven_lokalen_vijf_simus(verdelen):
    """Zoals in het demobestand: 7 lokalen, 5 verschillende simu's (2 staan dubbel), geen uitsluitingen."""
    def wijzig(b):
        b["Simu"] = b["Simu"][:6] + [b["Simu"][1], b["Simu"][2]]
        for rij in b["Studenten"][1:]:
            rij[5] = rij[6] = ""
        b["Instellingen"] = rc.instellingen_matrix({"verdelen": verdelen})
    return wijzig


def test_lokalen_evenredig_vullen_bij_te_weinig_simus():
    from collections import Counter
    r = concept(zeven_lokalen_vijf_simus("Evenredig"))
    per = Counter(x["Lokaal"] for x in rijen(r) if x["bijzheden"] != rc.VRIJ)
    assert len(per) == 7 and sum(per.values()) == 61 and max(per.values()) - min(per.values()) <= 3
    assert {"Fien", "Hans"} <= {x["Beoordelaar"] for x in rijen(r)}  # ook de beoordelaars van het laatste lokaal
    assert not any("krijgt niemand" in m[1] for m in r["meldingen"])


def test_op_volgorde_vullen_en_lokaal_zonder_iemand_krijgt_eigen_waarschuwing():
    r = concept(zeven_lokalen_vijf_simus("Op volgorde"))
    niemand = [m[1] for m in r["meldingen"] if "krijgt niemand" in m[1]]
    assert niemand and all("minder simu's dan lokalen" in m for m in niemand)
    assert any("C2 op 15-12-2026 (Fien → Hans)" in m for m in niemand)  # wie 'verdwijnt' staat er nu bij

    def niemand_speelt_i1(b):
        b["Simu"][0].append("Kan spelen")
        for rij in b["Simu"][1:]:
            rij.append("Q 1, R 1, R 2, Q 2")
    r = plan(wijzig=niemand_speelt_i1)
    assert any("Lokaal C1.39 op 14-04-2026 (Eef → Fien) krijgt niemand: er is op geen enkel moment een simucliënt" in m[1]
               for m in r["meldingen"])
    r = plan()  # genoeg simu's: geen waarschuwing
    assert not any("krijgt niemand" in m[1] for m in r["meldingen"])


def test_concept_beoordelaars_met_tijdvakken_in_keten():
    def tijdvakken(b):
        blad = b["Concept"]
        i = [k for k, r in enumerate(blad) if r[0] == "inzet"][0]
        blad[i + 4][1] = "Eef 10.00-12.00"           # Eef alleen 's ochtends
        blad.insert(i + 5, ["", "Dorus van 12.00 tot 15.20"])  # sluit aan op Eef
        blad.insert(i + 6, ["", "Lot vanaf 15.20"])          # sluit aan op Dorus
    r = concept(tijdvakken)
    tekst = " ".join(m[1] for m in r["meldingen"])
    assert "C2 Eef (10:00-12:00) → Dorus (12:00-15:20) → Lot (vanaf 15:20)" in tekst
    per = {x["Beoordelaar"] for x in rijen(r) if x["Beoordelaar"] in ("Eef", "Dorus", "Lot")}
    assert per == {"Eef", "Dorus", "Lot"} and len({x["Lokaal"] for x in rijen(r) if x["Beoordelaar"] in per}) == 1
