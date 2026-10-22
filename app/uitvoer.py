"""Uitvoer van de app: Excel-werkmap, PDF's om te printen/publiceren en een leeg sjabloon."""
from __future__ import annotations

import datetime as dt
from html import escape

from PySide6.QtCore import QMarginsF
from PySide6.QtGui import QFont, QPageLayout, QPageSize, QPdfWriter, QTextDocument

import rooster_core as rc

DAGEN = ["maandag", "dinsdag", "woensdag", "donderdag", "vrijdag", "zaterdag", "zondag"]
STUDENTEN_KOP = ["Studentnummer", "Voornaam", "Tussenvoegsel", "Achternaam", "klas", "Niet inroosteren bij SB-docent",
                 "Niet inroosteren bij de vaardighedendocent", "TTV", "IsHerkanser"] + rc.EERSTE_KOP
SLOTS_KOP = ["Datum", "Tijd", "Lokaal", "Casus", "Vaardigheid", "Casus na pauze"]
CSS = """
body { font-family: Arial, Helvetica, sans-serif; color: #0a0a0a; }
h1 { font-size: 18pt; font-weight: 600; margin: 0 0 2pt 0; }
p.sub { color: #737373; font-size: 10pt; margin: 0 0 12pt 0; }
table { border-collapse: collapse; }
th { background: #f5f5f5; color: #404040; font-weight: 600; text-align: left; border-bottom: 1px solid #d4d4d4; }
td { border-bottom: 1px solid #e5e5e5; }
"""


def dag_tekst(serie: int) -> str:
    d = dt.date(1899, 12, 30) + dt.timedelta(days=serie)
    return f"{DAGEN[d.weekday()]} {rc.datum_tekst(serie)}"


def _tabel(kop: list, rijen: list) -> str:
    th = "".join(f"<th>{escape(str(k))}</th>" for k in kop)
    tr = "".join("<tr>" + "".join(f"<td>{escape(rc.tekst(c))}</td>" for c in rij) + "</tr>" for rij in rijen)
    return f"<table width='100%' cellpadding='6' cellspacing='0'><thead><tr>{th}</tr></thead>{tr}</table>"


def html_uitdraai(titel: str, matrix: list) -> str:
    """Voor studenten: alleen naam, lokaal en tijd."""
    return (f"<style>{CSS}</style><h1>{escape(titel)}</h1>"
            f"<p class='sub'>{len(matrix) - 1} studenten</p>{_tabel(matrix[0], matrix[1:])}")


def html_rooster(titel: str, matrix: list) -> str:
    """Voor docenten: per dag en lokaal een eigen pagina (om bij het lokaal op te hangen)."""
    kop = matrix[0]
    i = {k: kop.index(k) for k in kop}
    groepen: dict = {}
    niet = []
    for rij in matrix[1:]:
        if rij[i["bijzheden"]] == "NIET INGEROOSTERD":
            niet.append(rij)
        else:
            groepen.setdefault((rij[i["Datum"]], rij[i["Lokaal"]]), []).append(rij)
    delen = []
    for n, ((datum, lokaal), rijen) in enumerate(sorted(groepen.items(), key=lambda g: (g[0][0], rc.tekst(g[0][1]).lower()))):
        rijen.sort(key=lambda r: r[i["Tijd"]])
        casussen = sorted({rc.tekst(r[i["Casus"]]) for r in rijen if rc.tekst(r[i["Casus"]])})
        regels = [[f"{rc.tijd_tekst(rc.naar_minuten(r[i['Tijd']]))}–{rc.tijd_tekst(rc.naar_minuten(r[i['Eindtijd']]))}",
                   " ".join(rc.tekst(r[i[k]]) for k in ("Voornaam", "vv", "Achternaam") if rc.tekst(r[i[k]])),
                   r[i["stnr"]], r[i["klas"]], r[i["Casus"]], r[i["Beoordelaar"]], r[i["simucliënt"]], r[i["bijzheden"]]]
                  for r in rijen]
        breuk = " style='page-break-before: always'" if n else ""
        delen.append(f"<h1{breuk}>Lokaal {escape(rc.tekst(lokaal))} · {escape(dag_tekst(datum))}</h1>"
                     f"<p class='sub'>{escape(titel)} · {len(rijen)} studenten · casus {escape(', '.join(casussen) or '–')}</p>"
                     + _tabel(["Tijd", "Student", "Nr.", "Klas", "Casus", "Beoordelaar", "Simucliënt", "Bijzonderheden"], regels))
    if niet:
        delen.append("<h1 style='page-break-before: always'>Niet ingeroosterd</h1><p class='sub'>Zie het blad Meldingen.</p>"
                     + _tabel(["Student", "Nr.", "Klas"], [[" ".join(rc.tekst(r[i[k]]) for k in ("Voornaam", "vv", "Achternaam")
                                                                   if rc.tekst(r[i[k]])), r[i["stnr"]], r[i["klas"]]] for r in niet]))
    return f"<style>{CSS}</style>" + "".join(delen)


def bewaar_pdf(html: str, pad: str, liggend: bool = False) -> None:
    pdf = QPdfWriter(pad)
    pdf.setPageSize(QPageSize(QPageSize.A4))
    pdf.setPageOrientation(QPageLayout.Landscape if liggend else QPageLayout.Portrait)
    pdf.setResolution(300)
    pdf.setPageMargins(QMarginsF(15, 15, 15, 15), QPageLayout.Millimeter)
    pdf.setTitle("Toetsrooster")
    doc = QTextDocument()
    doc.documentLayout().setPaintDevice(pdf)  # punten op PDF-resolutie, niet schermresolutie
    doc.setDefaultFont(QFont("Arial", 10))
    doc.setHtml(html)
    doc.setPageSize(pdf.pageLayout().paintRectPixels(pdf.resolution()).size().toSizeF())
    doc.print_(pdf)


def bewaar_werkmap(bron: str, doel: str, bladen: dict) -> None:
    """Kopie van de bronwerkmap met de nieuwe bladen erin (het origineel blijft onaangeroerd)."""
    from openpyxl import load_workbook
    wb = load_workbook(bron)
    rc.schrijf_bladen(wb, bladen)
    wb.save(doel)


def maak_sjabloon(pad: str) -> None:
    """Lege werkmap met de juiste bladen en kolommen, om zelf in te vullen."""
    from openpyxl import Workbook
    s = rc.STANDAARD
    wb = Workbook()
    wb.remove(wb.active)
    rc.schrijf_bladen(wb, {
        s["blad_studenten"]: [STUDENTEN_KOP],
        s["blad_slots1"]: [SLOTS_KOP],
        s["blad_slots_her"]: [SLOTS_KOP],
        s["blad_beo"]: [["Datum", "Tijd", "Beoordelaar", "Casus", "Lokaal"]],
        s["blad_simu"]: [["Datum", "Tijd", "simucliënt", "Casus", "Lokaal"]],
        rc.INSTELLINGEN_BLAD: rc.instellingen_matrix(),
    })
    wb.save(pad)
