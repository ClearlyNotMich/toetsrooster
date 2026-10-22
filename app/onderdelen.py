"""Herbruikbare UI-onderdelen: schakelaar, gesegmenteerde keuze, statistiekkaart en het instellingenformulier."""
from __future__ import annotations

from PySide6.QtCore import Property, QDate, QEasingCurve, QPropertyAnimation, QRectF, QSize, Qt, QTime, Signal
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import (QAbstractButton, QButtonGroup, QComboBox, QDateEdit, QDialog, QDialogButtonBox,
                               QFrame, QGridLayout, QListWidget, QListWidgetItem,
                               QHBoxLayout, QLabel, QLineEdit, QPushButton, QSpinBox, QTimeEdit, QVBoxLayout, QWidget)

import rooster_core as rc
from thema import KLEUR


def label(tekst: str, naam: str = "", wrap: bool = False) -> QLabel:
    lbl = QLabel(tekst)
    if naam:
        lbl.setObjectName(naam)
    lbl.setWordWrap(wrap)
    return lbl


def lijn() -> QFrame:
    f = QFrame()
    f.setObjectName("lijn")
    return f


class Schakelaar(QAbstractButton):
    """Aan/uit-schakelaar (zoals shadcn Switch)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(36, 20)
        self._pos = 0.0
        self._anim = QPropertyAnimation(self, b"pos", self, duration=120, easingCurve=QEasingCurve.OutCubic)
        self.toggled.connect(self._beweeg)

    def _beweeg(self, aan: bool):
        self._anim.stop()
        self._anim.setEndValue(1.0 if aan else 0.0)
        self._anim.start()

    def setChecked(self, aan: bool):  # noqa: N802 - Qt-naam
        super().setChecked(aan)
        self._anim.stop()
        self._pos = 1.0 if aan else 0.0
        self.update()

    def _get_pos(self):
        return self._pos

    def _set_pos(self, v):
        self._pos = v
        self.update()

    pos = Property(float, _get_pos, _set_pos)

    def sizeHint(self):  # noqa: N802
        return QSize(36, 20)

    def paintEvent(self, _):  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        uit, aan = QColor(KLEUR["rand_sterk"]), QColor(KLEUR["primair"])
        kleur = QColor(int(uit.red() + (aan.red() - uit.red()) * self._pos),
                       int(uit.green() + (aan.green() - uit.green()) * self._pos),
                       int(uit.blue() + (aan.blue() - uit.blue()) * self._pos))
        if not self.isEnabled():
            kleur.setAlpha(110)
        p.setPen(Qt.NoPen)
        p.setBrush(kleur)
        p.drawRoundedRect(QRectF(0, 0, 36, 20), 10, 10)
        p.setBrush(QColor("#ffffff"))
        p.drawEllipse(QRectF(2 + 16 * self._pos, 2, 16, 16))


class Segment(QFrame):
    """Gesegmenteerde keuze: één van een paar knoppen is actief."""
    gewijzigd = Signal(str)

    def __init__(self, opties: list[tuple[str, str]], parent=None):
        super().__init__(parent)
        self.setObjectName("segment")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(3, 3, 3, 3)
        lay.setSpacing(2)
        self.groep = QButtonGroup(self)
        for i, (waarde, tekst) in enumerate(opties):
            k = QPushButton(tekst, objectName="segmentknop", checkable=True, cursor=Qt.PointingHandCursor)
            k.setProperty("waarde", waarde)
            k.setChecked(i == 0)
            self.groep.addButton(k)
            lay.addWidget(k)
        self.groep.buttonToggled.connect(lambda k, aan: aan and self.gewijzigd.emit(k.property("waarde")))

    def waarde(self) -> str:
        return self.groep.checkedButton().property("waarde")


class StatKaart(QFrame):
    def __init__(self, titel: str, parent=None):
        super().__init__(parent)
        self.setObjectName("kaart")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(4)
        lay.addWidget(label(titel, "statlabel"))
        self.waarde = label("–", "statwaarde")
        lay.addWidget(self.waarde)
        self.sub = label(" ", "uitleg")
        lay.addWidget(self.sub)

    def zet(self, waarde: str, sub: str = " ", kleur: str | None = None):
        self.waarde.setText(waarde)
        self.waarde.setStyleSheet(f"color: {kleur};" if kleur else "")
        self.sub.setText(sub)


class InstellingenFormulier(QWidget):
    """Formulier dat zichzelf opbouwt uit rc.INSTELLINGEN (één bron voor app, Excel en scripts)."""
    gewijzigd = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("instellingenInhoud")
        self.velden: dict[str, QWidget] = {}
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(28)
        for i, groep in enumerate(rc.GROEPEN):
            if i:
                lay.addWidget(lijn())
            lay.addLayout(self._groep(groep, [x for x in rc.INSTELLINGEN if x["groep"] == groep]))
        lay.addStretch()
        self.herstel()

    # ---- opbouw

    def _groep(self, groep: str, items: list) -> QHBoxLayout:
        rij = QHBoxLayout()
        rij.setSpacing(32)
        links = QVBoxLayout()
        links.setSpacing(4)
        links.addWidget(label(groep, "legenda"))
        links.addWidget(label(rc.GROEPEN[groep], "gedempt", wrap=True))
        links.addStretch()
        box = QWidget()
        box.setFixedWidth(240)
        box.setLayout(links)
        rij.addWidget(box, 0, Qt.AlignTop)

        rechts = QGridLayout()
        rechts.setHorizontalSpacing(16)
        rechts.setVerticalSpacing(18)
        rechts.setColumnStretch(0, 1)
        rechts.setColumnStretch(1, 1)
        r = 0
        kolom = 0
        for x in items:
            w = self._veld(x)
            self.velden[x["sleutel"]] = w
            breed = isinstance(w, QComboBox) and (x["soort"] == "getal" or len(x["uitleg"]) > 60) \
                or isinstance(w, Schakelaar) or x["soort"] == "pauzes"
            if breed:
                if kolom:
                    r, kolom = r + 1, 0
                if isinstance(w, Schakelaar):
                    rechts.addWidget(self._schakelveld(x["label"], x["uitleg"], w), r, 0, 1, 2)
                else:
                    rechts.addLayout(self._veldblok(x, w), r, 0, 1, 2)
                r += 1
                continue
            rechts.addLayout(self._veldblok(x, w), r, kolom, Qt.AlignTop)
            kolom = 1 - kolom
            r += kolom == 0
        rechts.setRowStretch(r + 1, 1)  # extra hoogte onderaan, niet in de velden
        rij.addLayout(rechts, 1)
        return rij

    def _veld(self, x: dict) -> QWidget:
        if x["soort"] == "getal" and x["max"] - x["min"] < 5:  # paar mogelijkheden: keuzelijst
            w = QComboBox()
            w.addItems([str(n) for n in range(x["min"], x["max"] + 1)])
            w.currentIndexChanged.connect(self.gewijzigd)
        elif x["soort"] == "getal":
            w = QSpinBox(minimum=x["min"], maximum=x["max"])
            if "(min)" in x["label"]:
                w.setSuffix(" min")
            w.valueChanged.connect(self.gewijzigd)
        elif x["soort"] == "tijd":
            w = QTimeEdit(displayFormat="HH:mm")
            w.timeChanged.connect(self.gewijzigd)
        elif x["soort"] == "keuze" and x["opties"] == rc.JA_NEE:
            w = Schakelaar()
            w.toggled.connect(self.gewijzigd)
        elif x["soort"] == "keuze":
            w = QComboBox()
            w.addItems(x["opties"])
            w.currentIndexChanged.connect(self.gewijzigd)
        else:  # tekst en pauzes
            w = QLineEdit()
            if x["soort"] == "pauzes":
                w.setPlaceholderText("bijv. 11:15-11:40, 13:00-13:55 (leeg = geen pauze)")
            w.textChanged.connect(self.gewijzigd)
        if isinstance(w, (QSpinBox, QTimeEdit)):
            w.lineEdit().setTextMargins(6, 0, 6, 0)  # QSS-padding werkt niet op het binnenveld
        if x["uitleg"]:
            w.setToolTip(x["uitleg"])
        return w

    def _veldblok(self, x: dict, w: QWidget) -> QVBoxLayout:
        v = QVBoxLayout()
        v.setSpacing(6)
        naam = x["label"].replace(" (min)", "")
        v.addWidget(label(naam, "veldlabel"))
        v.addWidget(w)
        if x["uitleg"] and not isinstance(w, QSpinBox):
            v.addWidget(label(x["uitleg"], "uitleg", wrap=True))
        return v

    def _schakelveld(self, titel: str, uitleg: str, w: QWidget) -> QFrame:
        kaart = QFrame(objectName="kaart")
        h = QHBoxLayout(kaart)
        h.setContentsMargins(14, 12, 14, 12)
        tekst = QVBoxLayout()
        tekst.setSpacing(2)
        tekst.addWidget(label(titel, "veldlabel"))
        tekst.addWidget(label(uitleg, "uitleg", wrap=True))
        h.addLayout(tekst, 1)
        h.addWidget(w, 0, Qt.AlignVCenter)
        return kaart

    # ---- waarden

    def waarden(self) -> dict:
        """Sleutel -> waarde zoals in het blad Instellingen (tijd als tekst 09:40)."""
        uit = {}
        for x in rc.INSTELLINGEN:
            w = self.velden[x["sleutel"]]
            if x["soort"] == "getal":
                uit[x["sleutel"]] = int(w.currentText()) if isinstance(w, QComboBox) else w.value()
            elif x["soort"] == "tijd":
                uit[x["sleutel"]] = rc.tijd_tekst(w.time().msecsSinceStartOfDay() // 60_000)
            elif isinstance(w, Schakelaar):
                uit[x["sleutel"]] = "Ja" if w.isChecked() else "Nee"
            elif isinstance(w, QComboBox):
                uit[x["sleutel"]] = w.currentText()
            else:
                uit[x["sleutel"]] = w.text().strip()
        return uit

    def zet(self, ruw: dict) -> None:
        """Vult het formulier met ruwe waarden (bijv. uit rc.instellingen_waarden). Onbekende waarden -> standaard."""
        self.blockSignals(True)
        for x in rc.INSTELLINGEN:
            w, v = self.velden[x["sleutel"]], ruw.get(x["sleutel"], x["standaard"])
            if x["soort"] == "getal":
                t = rc.tekst(v)
                n = int(t) if t.isdigit() and x["min"] <= int(t) <= x["max"] else x["standaard"]
                w.setCurrentText(str(n)) if isinstance(w, QComboBox) else w.setValue(n)
            elif x["soort"] == "tijd":
                m = rc.naar_minuten(v)
                m = m if m is not None else rc.naar_minuten(x["standaard"])
                w.setTime(QTime(m // 60, m % 60))
            elif x["soort"] == "pauzes":
                pz = rc.lees_pauzes(v)
                w.setText(rc.pauzes_tekst(pz) if pz is not None else rc.tekst(v))
            else:
                opties = [o for o in x["opties"] if rc.norm(o) == rc.norm(v)]
                waarde = opties[0] if opties else (rc.tekst(v) if x["soort"] == "tekst" and rc.tekst(v) else x["standaard"])
                if isinstance(w, Schakelaar):
                    w.setChecked(waarde == "Ja")
                elif isinstance(w, QComboBox):
                    w.setCurrentText(waarde)
                else:
                    w.setText(waarde)
        self.blockSignals(False)
        self.gewijzigd.emit()

    def herstel(self) -> None:
        self.zet(rc.STANDAARD)


class SimuImport(QDialog):
    """Kies een datumkolom uit het beschikbaarheidsoverzicht en vink de simucliënten aan voor de toetsdag."""

    def __init__(self, kolommen: list, datum: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Simucliënten importeren")
        self.setMinimumSize(520, 560)
        self.kolommen = kolommen
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(12)
        lay.addWidget(label("Simucliënten importeren", "legenda"))
        lay.addWidget(label("Kies de kolom van de toetsdag. Wie in die kolom beschikbaar is, staat hieronder; de eerste "
                            "‘nodig’ zijn alvast aangevinkt. Ze komen in het blad Simu voor de gekozen datum.", "gedempt", wrap=True))
        rij = QHBoxLayout()
        kolom_v, datum_v = QVBoxLayout(), QVBoxLayout()
        kolom_v.addWidget(label("Kolom in overzicht", "veldlabel"))
        self.kolom = QComboBox()
        self.kolom.addItems([k["titel"] for k in kolommen])
        kolom_v.addWidget(self.kolom)
        datum_v.addWidget(label("Datum toetsdag", "veldlabel"))
        self.datum = QDateEdit(calendarPopup=True, displayFormat="dd-MM-yyyy")
        self.datum.setDate(QDate(1899, 12, 30).addDays(datum))
        datum_v.addWidget(self.datum)
        rij.addLayout(kolom_v, 2)
        rij.addLayout(datum_v, 1)
        lay.addLayout(rij)
        self.lijst = QListWidget()
        self.lijst.setObjectName("vinklijst")
        lay.addWidget(self.lijst, 1)
        self.telling = label("", "uitleg")
        lay.addWidget(self.telling)
        knoppen = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        knoppen.button(QDialogButtonBox.Ok).setText("In blad Simu zetten")
        knoppen.button(QDialogButtonBox.Ok).setObjectName("primair")
        knoppen.button(QDialogButtonBox.Cancel).setText("Annuleren")
        knoppen.accepted.connect(self.accept)
        knoppen.rejected.connect(self.reject)
        lay.addWidget(knoppen)
        self.kolom.currentIndexChanged.connect(self._vul)
        self.lijst.itemChanged.connect(self._tel)
        # Voorkeuze: de kolom met dezelfde datum als de toetsdag.
        import uitvoer
        passend = [i for i, k in enumerate(kolommen) if uitvoer.datum_bij(k["dag_maand"], datum) == datum]
        self.kolom.setCurrentIndex(passend[0] if passend else 0)
        self._vul()

    def _vul(self, *_):
        k = self.kolommen[self.kolom.currentIndex()]
        self.lijst.blockSignals(True)
        self.lijst.clear()
        nodig = k["nodig"] if k["nodig"] is not None else len(k["simus"])
        aan = 0
        for s in k["simus"]:
            extra = "" if rc.norm(s["tekst"]) == "x" else f"  ·  {s['tekst']}"
            item = QListWidgetItem(s["naam"] + extra)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            vink = s["zeker"] and aan < nodig
            aan += vink
            item.setCheckState(Qt.Checked if vink else Qt.Unchecked)
            item.setData(Qt.UserRole, s)
            self.lijst.addItem(item)
        self.lijst.blockSignals(False)
        self._tel()

    def _tel(self, *_):
        k = self.kolommen[self.kolom.currentIndex()]
        n = len(self.gekozen())
        nodig = f"nodig: {k['nodig']}" if k["nodig"] is not None else "aantal nodig onbekend"
        self.telling.setText(f"{n} gekozen · {nodig}" + (f" · tijden in overzicht: {k['tijd']}" if k["tijd"] else ""))

    def gekozen(self) -> list:
        return [self.lijst.item(i).data(Qt.UserRole) for i in range(self.lijst.count())
                if self.lijst.item(i).checkState() == Qt.Checked]

    def gekozen_datum(self) -> int:
        return QDate(1899, 12, 30).daysTo(self.datum.date())
