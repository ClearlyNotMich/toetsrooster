"""Toetsrooster — desktop-app (Qt6). Start: dubbelklik op het programma.

Leest dezelfde Excel-werkmap als de Office Scripts en gebruikt dezelfde logica
(rooster_core.py). Het origineel wordt nooit overschreven: het resultaat wordt
als nieuw bestand opgeslagen (openpyxl zou de scriptknoppen verwijderen).

Opbouw: rooster_core (logica) · uitvoer (Excel/PDF/sjabloon) · thema (uiterlijk)
· onderdelen (UI-bouwstenen) · dit bestand (venster en schermen).
"""
from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (QApplication, QButtonGroup, QFileDialog, QFrame, QHBoxLayout, QHeaderView, QMainWindow,
                               QMessageBox, QPushButton, QScrollArea, QStackedWidget, QTableWidget, QTableWidgetItem,
                               QTabWidget, QVBoxLayout, QWidget)

import rooster_core as rc
import thema
import uitvoer
from onderdelen import InstellingenFormulier, Segment, SimuImport, StatKaart, label
from thema import KLEUR

HULP = """
<style>li { margin-bottom: 6px; } h3 { margin-top: 18px; }</style><h3>Zo maak je een rooster</h3>
<ol>
<li><b>Vul de werkmap.</b> Begin met <i>Nieuw sjabloon…</i> in de zijbalk, of gebruik de werkmap van vorige keer:
  <ul>
  <li><b>Studenten</b> — één rij per student. <i>TTV</i> = Ja voor tijdverlenging, <i>Voorkeur</i> = Ochtend/Middag/Vroeg/Laat,
      <i>IsHerkanser</i> = Ja voor de herkansing. In <i>Niet inroosteren bij …</i> zet je docenten die deze student niet mogen
      beoordelen (scheiden met , ; of /). Tekst in <i>Opmerkingen</i> zoals ‘ttv bij uitvoering’ of ‘graag in de ochtend’
      wordt herkend en staat bij Meldingen om te controleren.</li>
  <li><b>Toetsdag_Kans1 / Toetsdag_Her</b> — één rij per lokaal per toetsdag: datum, lokaal, casus (en eventueel
      <i>Casus na pauze</i>), vaardigheid en beoordelaar. Wisselt de beoordelaar halverwege, vul dan <i>Beoordelaar 2</i>
      en <i>Wissel om</i> in.</li>
  <li><b>Of in lijstvorm</b> — één blad met in kolom A de kopjes <i>datum, inzet, tijden, pauzes, lokalen, casussen, simu's</i>
      en in kolom B de waarden eronder, zoals je het opschrijft. Uit een ander bestand: <i>Concept laden…</i> in de zijbalk.
      ‘ochtend tot 13.00’ en ‘middag vanaf 13.30’ delen een lokaal; een naam met (opmerking) is reserve.</li>
  <li><b>Simu</b> — één rij per simucliënt per toetsdag, eventueel met <i>Vanaf</i>/<i>Tot</i>.
      Sneller: <i>Simu's importeren…</i> in de zijbalk neemt ze over uit het overzicht ‘Beschikbaarheid simu's’.</li>
  </ul></li>
<li><b>Open de werkmap</b> hier (download hem eerst uit OneDrive/SharePoint).</li>
<li>Controleer de <b>instellingen</b>: eerste en laatste toets, toetsduur, wisseltijd en pauzes. Daaruit worden alle
  tijdslots gemaakt (standaard elke 20 minuten van 09:40 tot 17:00, met drie pauzes). Bij <i>Simu's wisselen van lokaal</i> kies je of simu's na elke pauze of na elke toets een lokaal doorschuiven.</li>
<li>Kies <b>Eerste kans</b> of <b>Herkansing</b> en klik op <b>Rooster maken</b>.
  Kijk bij <i>Meldingen</i> of iedereen een plek heeft en of de opmerkingen goed zijn gelezen.</li>
<li><b>Exporteer</b>:
  <ul>
  <li><b>Excel opslaan</b> — een nieuwe werkmap met het rooster (inclusief grijze <i>Vrije plek</i>-rijen), de uitdraai en de meldingen.</li>
  <li><b>PDF voor docenten</b> — per lokaal en dag een pagina om op te hangen, zonder vrije plekken.</li>
  <li><b>PDF voor studenten</b> — alleen naam, lokaal en tijd; geschikt om te publiceren.</li>
  </ul></li>
</ol>
<h3>Liever in Excel Online?</h3>
<p>De knoppen op het eerste blad van de werkmap doen hetzelfde (zie LEESMIJ). Ze gebruiken het blad
<i>Instellingen</i>; de app schrijft jouw instellingen daarin bij <i>Excel opslaan</i>.</p>
<h3>Iets klopt niet?</h3>
<p>Studenten die niet passen staan onderaan het rooster als <i>NIET INGEROOSTERD</i> en in <i>Meldingen</i>.
Meestal zijn er te weinig plekken, sluiten de uitsluitingen alle beoordelaars van een student uit, of zijn er te weinig
simucliënten in een blok. Pas de werkmap of de instellingen aan en maak het rooster opnieuw.</p>
"""


# Nettere kolomkoppen in de app (de werkmap houdt de oorspronkelijke namen).
KOPPEN = {"simucliënt": "Simucliënt", "stnr": "Studentnr.", "vv": "Tussenv.", "klas": "Klas", "bijzheden": "Bijzonderheden",
          "Eindtijd": "Eind"}


def toon(kop: str, waarde) -> str:
    """Celwaarde netjes als tekst (datums en tijden zoals in Excel)."""
    k = rc.norm(kop)
    if isinstance(waarde, (int, float)) and not isinstance(waarde, bool):
        if k in ("datum", "eerstedatum"):
            return rc.datum_tekst(int(waarde))
        if k in ("tijd", "eindtijd", "eerstetijd"):
            return rc.tijd_tekst(rc.naar_minuten(waarde))
    return rc.tekst(waarde)


def pagina(titel: str, uitleg: str) -> tuple[QWidget, QVBoxLayout, QHBoxLayout]:
    """Lege pagina met titel en uitleg; geeft (pagina, inhoud-layout, acties-layout rechtsboven)."""
    w = QWidget(objectName="inhoud")
    lay = QVBoxLayout(w)
    lay.setContentsMargins(40, 32, 40, 24)
    lay.setSpacing(20)
    kop = QHBoxLayout()
    tekst = QVBoxLayout()
    tekst.setSpacing(4)
    tekst.addWidget(label(titel, "paginatitel"))
    tekst.addWidget(label(uitleg, "gedempt", wrap=True))
    kop.addLayout(tekst, 1)
    acties = QHBoxLayout()
    acties.setSpacing(8)
    kop.addLayout(acties)
    lay.addLayout(kop)
    return w, lay, acties


class Venster(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Toetsrooster")
        self.resize(1280, 820)
        self.setMinimumSize(1020, 640)
        self.pad: str | None = None
        self.bladen: dict | None = None
        self.resultaat: dict | None = None

        midden = QWidget(objectName="inhoud")
        self.setCentralWidget(midden)
        h = QHBoxLayout(midden)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(0)
        h.addWidget(self._zijbalk())
        self.paginas = QStackedWidget()
        self.paginas.addWidget(self._rooster_pagina())
        self.paginas.addWidget(self._instellingen_pagina())
        self.paginas.addWidget(self._hulp_pagina())
        h.addWidget(self.paginas, 1)
        self.nav.buttons()[0].setChecked(True)
        self.statusBar().showMessage("Open een werkmap om te beginnen.")
        self.instellingen.gewijzigd.connect(self.verouderd)
        self.modus.gewijzigd.connect(self.verouderd)
        self.toon_samenvatting()
        self.toon_leeg()

    # ---------------------------------------------------------------- opbouw

    def _zijbalk(self) -> QFrame:
        z = QFrame(objectName="zijbalk")
        z.setFixedWidth(232)
        lay = QVBoxLayout(z)
        lay.setContentsMargins(14, 18, 14, 16)
        lay.setSpacing(4)
        merk = QHBoxLayout()
        merk.setSpacing(10)
        m = label("T", "merk")
        m.setFixedSize(28, 28)
        m.setAlignment(Qt.AlignCenter)
        merk.addWidget(m)
        merk.addWidget(label("Toetsrooster", "appnaam"), 1)
        lay.addLayout(merk)
        lay.addSpacing(18)
        lay.addWidget(label("MENU", "sectie"))
        self.nav = QButtonGroup(self)
        for i, tekst in enumerate(("Rooster", "Instellingen", "Hulp")):
            k = QPushButton(tekst, objectName="nav", checkable=True, cursor=Qt.PointingHandCursor)
            self.nav.addButton(k, i)
            lay.addWidget(k)
        self.nav.idClicked.connect(lambda i: self.paginas.setCurrentIndex(i))
        lay.addStretch()
        lay.addWidget(label("WERKMAP", "sectie"))
        self.lbl_bestand = label("Geen werkmap geopend", "bestandsnaam", wrap=True)
        lay.addWidget(self.lbl_bestand)
        self.lbl_bestand_info = label("", "uitleg", wrap=True)
        lay.addWidget(self.lbl_bestand_info)
        lay.addSpacing(8)
        open_ = QPushButton("Werkmap openen…", cursor=Qt.PointingHandCursor)
        open_.clicked.connect(self.kies_bestand)
        lay.addWidget(open_)
        sjabloon = QPushButton("Nieuw sjabloon…", cursor=Qt.PointingHandCursor)
        sjabloon.setToolTip("Lege werkmap met de juiste bladen en kolommen om zelf in te vullen.")
        sjabloon.clicked.connect(self.sjabloon)
        lay.addWidget(sjabloon)
        self.knop_concept = QPushButton("Concept laden…", cursor=Qt.PointingHandCursor)
        self.knop_concept.setToolTip("Toetsdag in lijstvorm (datum, inzet, tijden, pauzes, lokalen, casussen, simu's) "
                                     "uit een ander bestand in deze werkmap zetten.")
        self.knop_concept.clicked.connect(lambda: self.laad_concept())
        lay.addWidget(self.knop_concept)
        self.knop_import = QPushButton("Simu's importeren…", cursor=Qt.PointingHandCursor)
        self.knop_import.setToolTip("Simucliënten voor de toetsdag overnemen uit het overzicht ‘Beschikbaarheid simu's’.")
        self.knop_import.clicked.connect(lambda: self.importeer_simus())
        lay.addWidget(self.knop_import)
        return z

    def _rooster_pagina(self) -> QWidget:
        w, lay, acties = pagina("Rooster", "Kies de toets, maak het rooster en exporteer het om te printen of te publiceren.")
        self.knop_opslaan = QPushButton("Excel opslaan…", cursor=Qt.PointingHandCursor)
        self.knop_opslaan.setToolTip("Nieuwe werkmap met rooster, uitdraai, meldingen en instellingen. Het origineel blijft ongewijzigd.")
        self.knop_opslaan.clicked.connect(lambda: self.opslaan())
        self.knop_pdf_rooster = QPushButton("PDF voor docenten…", cursor=Qt.PointingHandCursor)
        self.knop_pdf_rooster.setToolTip("Per lokaal en dag een pagina met tijden, studenten, casus, beoordelaar en simucliënt.")
        self.knop_pdf_rooster.clicked.connect(lambda: self.pdf_rooster())
        self.knop_pdf = QPushButton("PDF voor studenten…", cursor=Qt.PointingHandCursor)
        self.knop_pdf.setToolTip("Alleen naam, lokaal en tijd — geschikt om te publiceren.")
        self.knop_pdf.clicked.connect(lambda: self.pdf())
        self.knop_maak = QPushButton("Rooster maken", objectName="primair", cursor=Qt.PointingHandCursor)
        self.knop_maak.clicked.connect(self.maak)
        for k in (self.knop_opslaan, self.knop_pdf_rooster, self.knop_pdf, self.knop_maak):
            acties.addWidget(k)

        balk = QHBoxLayout()
        self.modus = Segment([(k, m["naam"]) for k, m in rc.MODI.items()])
        self.modus_groep = self.modus.groep
        balk.addWidget(self.modus)
        balk.addSpacing(12)
        self.samenvatting = label("", "gedempt")
        balk.addWidget(self.samenvatting)
        wijzig = QPushButton("Wijzigen", objectName="link", cursor=Qt.PointingHandCursor)
        wijzig.clicked.connect(lambda: self.nav.button(1).click())
        balk.addWidget(wijzig)
        balk.addStretch()
        lay.addLayout(balk)

        stats = QHBoxLayout()
        stats.setSpacing(12)
        self.stat_in = StatKaart("Ingeroosterd")
        self.stat_waarsch = StatKaart("Waarschuwingen")
        self.stat_niet = StatKaart("Niet ingeroosterd")
        for s in (self.stat_in, self.stat_waarsch, self.stat_niet):
            stats.addWidget(s)
        lay.addLayout(stats)

        kaart = QFrame(objectName="kaart")
        kv = QVBoxLayout(kaart)
        kv.setContentsMargins(16, 8, 16, 8)
        self.kaart_stapel = QStackedWidget()
        leeg = QWidget()
        lv = QVBoxLayout(leeg)
        lv.addStretch()
        self.leeg_titel = label("", "legenda")
        self.leeg_tekst = label("", "gedempt", wrap=True)
        for x in (self.leeg_titel, self.leeg_tekst):
            x.setAlignment(Qt.AlignCenter)
            lv.addWidget(x)
        self.leeg_knop = QPushButton("Werkmap openen…", objectName="primair", cursor=Qt.PointingHandCursor)
        self.leeg_knop.clicked.connect(self.kies_bestand)
        lv.addSpacing(12)
        lv.addWidget(self.leeg_knop, 0, Qt.AlignCenter)
        lv.addStretch()
        self.kaart_stapel.addWidget(leeg)
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabBar().setDrawBase(False)
        self.tabel_rooster, self.tabel_uitdraai, self.tabel_meldingen = (self.maak_tabel() for _ in range(3))
        self.tabs.addTab(self.tabel_rooster, "Volledig rooster")
        self.tabs.addTab(self.tabel_uitdraai, "Uitdraai studenten")
        self.tabs.addTab(self.tabel_meldingen, "Meldingen")
        self.kaart_stapel.addWidget(self.tabs)
        kv.addWidget(self.kaart_stapel)
        lay.addWidget(kaart, 1)
        return w

    def _instellingen_pagina(self) -> QWidget:
        w, lay, acties = pagina("Instellingen", "Worden bij ‘Excel opslaan’ in het blad Instellingen bewaard, zodat de knoppen "
                                               "in Excel Online dezelfde regels gebruiken.")
        lay.setSpacing(24)
        herstel = QPushButton("Standaardwaarden", cursor=Qt.PointingHandCursor)
        herstel.clicked.connect(lambda: self.instellingen.herstel())
        acties.addWidget(herstel)
        self.instellingen = InstellingenFormulier()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        houder = QWidget(objectName="instellingenInhoud")
        hl = QHBoxLayout(houder)
        hl.setContentsMargins(0, 0, 16, 24)
        self.instellingen.setMaximumWidth(860)
        hl.addWidget(self.instellingen, 1, Qt.AlignTop)
        hl.addStretch(0)
        scroll.setWidget(houder)
        lay.addWidget(scroll, 1)
        return w

    def _hulp_pagina(self) -> QWidget:
        w, lay, _ = pagina("Hulp", "Van gegevens naar een rooster om te printen en te publiceren.")
        tekst = label(HULP, "hulp", wrap=True)
        tekst.setTextFormat(Qt.RichText)
        tekst.setMaximumWidth(760)
        tekst.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(tekst)
        lay.addWidget(scroll, 1)
        return w

    @staticmethod
    def maak_tabel() -> QTableWidget:
        t = QTableWidget()
        t.setEditTriggers(QTableWidget.NoEditTriggers)
        t.setSelectionBehavior(QTableWidget.SelectRows)
        t.setShowGrid(False)
        t.setFocusPolicy(Qt.NoFocus)
        t.verticalHeader().setVisible(False)
        t.verticalHeader().setDefaultSectionSize(36)
        t.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        t.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        t.horizontalHeader().setStretchLastSection(True)
        t.horizontalHeader().setHighlightSections(False)
        return t

    # ---------------------------------------------------------------- weergave

    def toon_samenvatting(self):
        c = self.concept() if self.bladen else None
        if c and c["d"]:
            s = rc.lees_instellingen(rc.instellingen_matrix(self.instellingen.waarden()), [])
            c = rc.lees_concept(self.bladen[rc.vind_concept(self.bladen)], "", s, [], [])
            self.samenvatting.setText(f"Concept {rc.datum_tekst(c['d'])} · {len({x['lokaal'] for x in c['slots']})} lokalen · "
                                      f"toets {s['duur']} min · TTV {s['ttv']} min · {rc.tijd_tekst(s['start'])}–"
                                      f"{rc.tijd_tekst(s['eind'])} · {len(s['pauzes'])} pauzes")
            return
        s = self.instellingen.waarden()
        j = s["jaar"]
        tekst = f"Jaar {j} · toets {s[f'duur{j}']} min · TTV {s[f'ttv{j}']} min · "
        pz = rc.lees_pauzes(s["pauzes"])
        tekst += f"{s['start']}–{s['eind']} · "
        tekst += (f"{len(pz)} pauze{'s' if len(pz) != 1 else ''}" if pz else "geen pauze") if pz is not None else "pauzes ongeldig"
        self.samenvatting.setText(tekst)

    def toon_leeg(self):
        open_ = self.bladen is not None
        self.leeg_titel.setText("Klaar om te roosteren" if open_ else "Nog geen werkmap geopend")
        self.leeg_tekst.setText("Controleer de instellingen en klik op ‘Rooster maken’." if open_ else
                                "Open de Excel-werkmap met studenten, de toetsdag en de simucliënten,\n"
                                "of begin met een nieuw sjabloon.")
        self.leeg_knop.setVisible(not open_)
        self.kaart_stapel.setCurrentIndex(0)
        for s in (self.stat_in, self.stat_waarsch, self.stat_niet):
            s.zet("–")
        self.knop_maak.setEnabled(open_)
        self.knop_import.setEnabled(open_)
        self.knop_concept.setEnabled(open_)
        for k in (self.knop_opslaan, self.knop_pdf, self.knop_pdf_rooster):
            k.setEnabled(False)

    def vul(self, tabel: QTableWidget, matrix: list):
        kop, data = matrix[0], matrix[1:]
        tabel.clear()
        tabel.setColumnCount(len(kop))
        tabel.setRowCount(len(data))
        tabel.setHorizontalHeaderLabels([KOPPEN.get(rc.tekst(k), rc.tekst(k)) for k in kop])
        for r, rij in enumerate(data):
            soort = rc.tekst(rij[0]) if kop == rc.MELDINGEN_KOP else ""
            niet = rc.NIET in rij
            vrij = rc.VRIJ in rij
            for c, waarde in enumerate(rij):
                item = QTableWidgetItem(toon(kop[c], waarde))
                if vrij:
                    item.setForeground(QColor(KLEUR["gedempt_tekst"]))
                    item.setBackground(QColor(KLEUR["gedempt"]))
                elif niet or soort == "Fout":
                    item.setForeground(QColor(KLEUR["fout"]))
                    item.setBackground(QColor(KLEUR["fout_zacht"]))
                elif soort == "Waarschuwing" and c == 0:
                    item.setForeground(QColor(KLEUR["let_op"]))
                elif soort == "Info" and c == 0:
                    item.setForeground(QColor(KLEUR["gedempt_tekst"]))
                tabel.setItem(r, c, item)
        tabel.resizeColumnsToContents()

    def verouderd(self, *_):
        self.toon_samenvatting()
        if self.resultaat:
            self.resultaat = None
            self.toon_leeg()
            self.leeg_titel.setText("Instellingen gewijzigd")
            self.leeg_tekst.setText("Klik opnieuw op ‘Rooster maken’ om het rooster bij te werken.")

    # ---------------------------------------------------------------- acties

    def kies_bestand(self):
        pad, _ = QFileDialog.getOpenFileName(self, "Werkmap openen", "", "Excel-werkmap (*.xlsx *.xlsm)")
        if pad:
            self.open(pad)

    def open(self, pad: str) -> bool:
        try:
            bladen = rc.lees_werkmap(pad)
        except Exception as e:  # noqa: BLE001 - toon elke leesfout aan de gebruiker
            QMessageBox.critical(self, "Kan werkmap niet openen", f"{pad}\n\n{e}\n\nIs het bestand nog geopend in Excel?")
            return False
        self.pad, self.bladen, self.resultaat = pad, bladen, None
        self.ingevoerd = {}  # in de app aangepaste invoerbladen (bijv. Simu na importeren); gaan mee bij opslaan
        self.instellingen.zet(rc.instellingen_waarden(bladen.get(rc.INSTELLINGEN_BLAD)))
        self.lbl_bestand.setText(Path(pad).name)
        self.toon_samenvatting()
        n = max(0, len(bladen.get(self.instellingen.waarden()["blad_studenten"], [])) - 1)
        self.lbl_bestand_info.setText(f"{n} rijen studenten · {len(bladen)} bladen")
        self.toon_leeg()
        self.statusBar().showMessage(f"Geopend: {pad}")
        return True

    def maak(self) -> dict:
        bladen = dict(self.bladen)
        bladen[rc.INSTELLINGEN_BLAD] = rc.instellingen_matrix(self.instellingen.waarden())
        r = rc.maak_rooster(bladen, self.modus.waarde())
        r["bladen"][rc.INSTELLINGEN_BLAD] = bladen[rc.INSTELLINGEN_BLAD]
        if not r["fouten"]:
            r["bladen"].update(self.ingevoerd)
        r["modus"] = self.modus.waarde()
        self.resultaat = r
        meld = r["bladen"][r["namen"]["meldingen"]]
        self.vul(self.tabel_meldingen, meld)
        waarsch = sum(1 for x in r["meldingen"] if x[0] == "Waarschuwing")
        self.tabs.setTabText(2, f"Meldingen ({len(meld) - 1})")
        self.kaart_stapel.setCurrentIndex(1)
        if r["fouten"]:
            for t in (self.tabel_rooster, self.tabel_uitdraai):
                t.clear(), t.setRowCount(0), t.setColumnCount(0)
            self.tabs.setCurrentWidget(self.tabel_meldingen)
            self.stat_in.zet("–", "Rooster niet gemaakt")
            self.stat_waarsch.zet(str(len(r["fouten"])), "fout(en) in de werkmap", KLEUR["fout"])
            self.stat_niet.zet("–")
            self.statusBar().showMessage("Los de fouten op in de werkmap en open hem opnieuw.")
        else:
            rooster = r["bladen"][r["namen"]["rooster"]]
            self.vul(self.tabel_rooster, rooster)
            self.vul(self.tabel_uitdraai, r["bladen"][r["namen"]["uitdraai"]])
            niet = sum(1 for rij in rooster if rc.NIET in rij)
            vrij = sum(1 for rij in rooster if rc.VRIJ in rij)
            totaal = len(rooster) - 1 - vrij
            self.stat_in.zet(f"{totaal - niet} / {totaal}", rc.MODI[r["modus"]]["naam"].lower()
                             + (f" · {vrij} vrije plekken" if vrij else ""))
            self.stat_waarsch.zet(str(waarsch), "zie Meldingen" if waarsch else "alles in orde",
                                  KLEUR["let_op"] if waarsch else None)
            self.stat_niet.zet(str(niet), "studenten zonder plek" if niet else "iedereen heeft een plek",
                               KLEUR["fout"] if niet else None)
            self.tabs.setCurrentWidget(self.tabel_rooster)
            self.statusBar().showMessage(r["meldingen"][0][1])
        for k in (self.knop_opslaan, self.knop_pdf, self.knop_pdf_rooster):
            k.setEnabled(not r["fouten"])
        return r

    def _doel(self, titel: str, naam: str, filter_: str, doel: str | None) -> str | None:
        if doel:
            return doel
        voorstel = str(Path(self.pad).with_name(naam))
        doel, _ = QFileDialog.getSaveFileName(self, titel, voorstel, filter_)
        return doel or None

    def opslaan(self, doel: str | None = None) -> str | None:
        doel = self._doel("Rooster opslaan als", f"{Path(self.pad).stem} - {self.resultaat['namen']['rooster']}.xlsx",
                          "Excel-werkmap (*.xlsx)", doel)
        if not doel:
            return None
        if Path(doel).resolve() == Path(self.pad).resolve():
            QMessageBox.warning(self, "Kies een andere naam",
                                "Het origineel wordt niet overschreven (de scriptknoppen zouden verdwijnen). Kies een nieuwe bestandsnaam.")
            return None
        try:
            uitvoer.bewaar_werkmap(self.pad, doel, self.resultaat["bladen"])
        except Exception as e:  # noqa: BLE001
            QMessageBox.critical(self, "Opslaan mislukt", f"{doel}\n\n{e}\n\nIs het bestand nog geopend in Excel?")
            return None
        self.statusBar().showMessage(f"Opgeslagen: {doel}")
        return doel

    def _bewaar_pdf(self, doel: str, html: str, liggend: bool) -> str | None:
        try:
            uitvoer.bewaar_pdf(html, doel, liggend)
        except Exception as e:  # noqa: BLE001
            QMessageBox.critical(self, "PDF maken mislukt", f"{doel}\n\n{e}")
            return None
        self.statusBar().showMessage(f"PDF opgeslagen: {doel}")
        return doel

    def pdf(self, doel: str | None = None) -> str | None:
        """PDF voor studenten: alleen naam, lokaal en tijd."""
        namen = self.resultaat["namen"]
        doel = self._doel("PDF voor studenten", f"{namen['uitdraai']}.pdf", "PDF (*.pdf)", doel)
        titel = f"Toetsrooster — {rc.MODI[self.resultaat['modus']]['naam']}"
        return doel and self._bewaar_pdf(doel, uitvoer.html_uitdraai(titel, self.resultaat["bladen"][namen["uitdraai"]]), False)

    def pdf_rooster(self, doel: str | None = None) -> str | None:
        """PDF voor docenten: per lokaal en dag een pagina."""
        namen = self.resultaat["namen"]
        doel = self._doel("PDF voor docenten", f"{namen['rooster']}.pdf", "PDF (*.pdf)", doel)
        titel = f"Toetsrooster {rc.MODI[self.resultaat['modus']]['naam'].lower()}"
        return doel and self._bewaar_pdf(doel, uitvoer.html_rooster(titel, self.resultaat["bladen"][namen["rooster"]]), True)

    def concept(self) -> dict | None:
        """Gegevens uit het conceptblad van de open werkmap (datum, aantal simu's nodig), of None."""
        naam = rc.vind_concept(self.bladen or {})
        if not naam:
            return None
        s = rc.lees_instellingen(rc.instellingen_matrix(self.instellingen.waarden()), [])
        return rc.lees_concept(self.bladen[naam], naam, s, [], [])

    def toetsdatum(self) -> int:
        """Datum uit het conceptblad of de eerste datum in het blad Toetsdag (anders vandaag)."""
        c = self.concept()
        if c and c["d"]:
            return c["d"]
        w = self.instellingen.waarden()
        dag = self.bladen.get(w[rc.MODI[self.modus.waarde()]["dag"]]) or []
        c = rc.kolom(dag[0], "datum") if dag else -1
        datums = [rc.naar_datum(rij[c]) for rij in dag[1:] if c >= 0 and rc.naar_datum(rc.cel(rij, c))]
        import datetime as dt
        return min(datums) if datums else (dt.date.today() - dt.date(1899, 12, 30)).days

    def importeer_simus(self, pad: str | None = None, kies=None) -> bool:
        """Simucliënten uit het beschikbaarheidsoverzicht in het blad Simu zetten. `kies` vervangt de dialoog (tests)."""
        if not pad:
            pad, _ = QFileDialog.getOpenFileName(self, "Beschikbaarheid simu's openen", str(Path(self.pad).parent),
                                                 "Excel-werkmap (*.xlsx *.xlsm)")
        if not pad:
            return False
        middag = rc.naar_minuten(self.instellingen.waarden()["middag"]) or 12 * 60
        try:
            kolommen = uitvoer.lees_beschikbaarheid(pad, middag)
        except Exception as e:  # noqa: BLE001
            QMessageBox.critical(self, "Kan overzicht niet lezen", f"{pad}\n\n{e}")
            return False
        if not kolommen:
            QMessageBox.warning(self, "Geen datums gevonden", "Het overzicht heeft geen kolommen met simucliënten.")
            return False
        c = self.concept()
        dlg = SimuImport(kolommen, self.toetsdatum(), self, nodig=c["nodig"] if c and c["nodig"] else None)
        if not (kies(dlg) if kies else dlg.exec()):
            return False
        if not dlg.gekozen():
            self.statusBar().showMessage("Niemand aangevinkt: het blad Simu is niet veranderd.")
            return False
        blad = self.instellingen.waarden()["blad_simu"]
        nieuw = uitvoer.simu_blad_met(self.bladen.get(blad), dlg.gekozen_datum(), dlg.gekozen())
        self.bladen[blad] = self.ingevoerd[blad] = nieuw
        self.verouderd()
        self.statusBar().showMessage(f"{len(dlg.gekozen())} simucliënt(en) voor {rc.datum_tekst(dlg.gekozen_datum())} in blad "
                                     f"{blad} gezet. Maak het rooster opnieuw; ‘Excel opslaan’ bewaart het blad.")
        return True

    def laad_concept(self, pad: str | None = None) -> bool:
        """Conceptblad uit een ander bestand in de open werkmap zetten (als blad 'Concept')."""
        if not pad:
            pad, _ = QFileDialog.getOpenFileName(self, "Concept openen", str(Path(self.pad).parent), "Excel-werkmap (*.xlsx *.xlsm)")
        if not pad:
            return False
        try:
            bron = rc.lees_werkmap(pad)
        except Exception as e:  # noqa: BLE001
            QMessageBox.critical(self, "Kan concept niet openen", f"{pad}\n\n{e}")
            return False
        naam = rc.vind_concept(bron)
        if not naam:
            QMessageBox.warning(self, "Geen concept gevonden", "Geen blad met in kolom A de kopjes ‘lokalen’ en ‘tijden’ "
                                "(of ‘inzet’), met de waarden eronder in kolom B.")
            return False
        # Het nieuwe concept vooraan, zodat het voor eventuele oudere conceptbladen gaat.
        self.bladen = {"Concept": bron[naam], **{k: v for k, v in self.bladen.items() if k != "Concept"}}
        self.ingevoerd["Concept"] = bron[naam]
        for k, v in bron.items():  # studenten of simu's uit het conceptbestand alleen als ze hier nog ontbreken
            if k != naam and rc.heeft_data(v) and not rc.heeft_data(self.bladen.get(k)):
                self.bladen[k] = self.ingevoerd[k] = v
        self.verouderd()
        c = self.concept()
        self.statusBar().showMessage(f"Concept geladen uit {Path(pad).name}" + (f" ({rc.datum_tekst(c['d'])})" if c and c["d"] else "")
                                     + ". Maak het rooster opnieuw; ‘Excel opslaan’ bewaart het als blad ‘Concept’.")
        return True

    def sjabloon(self, doel: str | None = None) -> str | None:
        if not doel:
            doel, _ = QFileDialog.getSaveFileName(self, "Nieuw sjabloon", "Toetsrooster sjabloon.xlsx", "Excel-werkmap (*.xlsx)")
        if not doel:
            return None
        uitvoer.maak_sjabloon(doel)
        self.statusBar().showMessage(f"Sjabloon opgeslagen: {doel} — vul het in en open het daarna hier.")
        return doel


def controle(invoer: str, map_: str) -> int:
    """Zelftest zonder vensters (ook voor het gebouwde programma): --controle WERKMAP UITVOERMAP."""
    app = QApplication.instance() or QApplication(sys.argv)  # noqa: F841
    v = Venster()
    if not v.open(invoer):
        return 2
    code = 0
    for knop in v.modus_groep.buttons():
        knop.setChecked(True)
        r = v.maak()
        doel = Path(map_) / f"controle-{r['namen']['rooster']}.xlsx"
        ok = not r["fouten"] and v.opslaan(str(doel)) and v.pdf(str(doel.with_suffix(".pdf"))) \
            and v.pdf_rooster(str(doel.with_name(doel.stem + "-docenten.pdf")))
        code = code or (0 if ok else 1)
        if sys.stdout:  # None in het Windows-venster-programma
            print(f"{r['meldingen'][0][1] if not r['fouten'] else r['fouten']} -> {doel}")
    if not v.sjabloon(str(Path(map_) / "controle-sjabloon.xlsx")):
        code = 1
    return code


def main() -> int:
    if len(sys.argv) == 4 and sys.argv[1] == "--controle":
        return controle(sys.argv[2], sys.argv[3])
    app = QApplication(sys.argv)
    thema.toepassen(app)
    v = Venster()
    v.show()
    if len(sys.argv) == 2 and Path(sys.argv[1]).exists():
        v.open(sys.argv[1])
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
