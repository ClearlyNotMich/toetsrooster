"""Uiterlijk van de app: kleuren en maten uit shadcn/ui (new-york v4, 'neutral'), vertaald naar Qt.

Eén neutrale grijsschaal, één donkere primaire kleur, 1px randen, 8–10px afronding,
36px hoge invoervelden. Kleur alleen voor status (waarschuwing/fout).
"""
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

KLEUR = {
    "achtergrond": "#ffffff",
    "tekst": "#0a0a0a",
    "gedempt": "#f5f5f5",
    "gedempt_tekst": "#737373",
    "rand": "#e5e5e5",
    "rand_sterk": "#d4d4d4",
    "ring": "#a1a1a1",
    "primair": "#171717",
    "primair_hover": "#2e2e2e",
    "primair_tekst": "#fafafa",
    "zijbalk": "#fafafa",
    "fout": "#dc2626",
    "fout_zacht": "#fef2f2",
    "let_op": "#b45309",
    "let_op_zacht": "#fffbeb",
    "goed": "#15803d",
}

STIJL = """
* {{ font-size: 13px; color: {tekst}; }}
QMainWindow, QWidget#inhoud, QScrollArea, QWidget#instellingenInhoud {{ background: {achtergrond}; border: none; }}
QToolTip {{ background: {primair}; color: {primair_tekst}; border: none; padding: 4px 8px; border-radius: 6px; }}

/* zijbalk */
QFrame#zijbalk {{ background: {zijbalk}; border-right: 1px solid {rand}; }}
QLabel#merk {{ background: {primair}; color: {primair_tekst}; border-radius: 6px; font-weight: 700; font-size: 12px; }}
QLabel#appnaam {{ font-size: 14px; font-weight: 600; }}
QLabel#sectie {{ color: {gedempt_tekst}; font-size: 11px; font-weight: 500; letter-spacing: 0.4px; }}
QLabel#bestandsnaam {{ font-weight: 500; }}
QPushButton#nav {{ text-align: left; padding: 0 10px; min-height: 32px; border: none; border-radius: 6px; background: transparent; }}
QPushButton#nav:hover {{ background: {gedempt}; }}
QPushButton#nav:checked {{ background: #ececec; font-weight: 600; }}

/* tekst */
QLabel#paginatitel {{ font-size: 22px; font-weight: 600; }}
QLabel#gedempt, QLabel#uitleg {{ color: {gedempt_tekst}; }}
QLabel#uitleg {{ font-size: 12px; }}
QLabel#legenda {{ font-size: 15px; font-weight: 600; }}
QLabel#veldlabel {{ font-weight: 500; }}

/* knoppen */
QPushButton {{ min-height: 36px; padding: 0 16px; border-radius: 8px; font-weight: 500;
              background: {achtergrond}; border: 1px solid {rand}; }}
QPushButton:hover {{ background: {gedempt}; }}
QPushButton:disabled {{ color: {ring}; }}
QPushButton#primair {{ background: {primair}; color: {primair_tekst}; border: 1px solid {primair}; }}
QPushButton#primair:hover {{ background: {primair_hover}; }}
QPushButton#primair:disabled {{ background: #a3a3a3; border-color: #a3a3a3; color: {primair_tekst}; }}
QPushButton#link {{ border: none; background: transparent; padding: 0; min-height: 0; color: {tekst};
                   text-decoration: underline; font-weight: 400; }}

/* gesegmenteerde keuze */
QFrame#segment {{ background: {gedempt}; border-radius: 8px; }}
QPushButton#segmentknop {{ min-height: 30px; padding: 0 14px; border: 1px solid transparent; border-radius: 6px;
                          background: transparent; color: {gedempt_tekst}; }}
QPushButton#segmentknop:checked {{ background: {achtergrond}; border-color: {rand}; color: {tekst}; }}

/* kaarten */
QFrame#kaart {{ background: {achtergrond}; border: 1px solid {rand}; border-radius: 10px; }}
QFrame#kaart QLabel {{ background: transparent; }}
QLabel#statlabel {{ color: {gedempt_tekst}; font-weight: 500; }}
QLabel#statwaarde {{ font-size: 24px; font-weight: 600; }}
QFrame#lijn {{ background: {rand}; max-height: 1px; min-height: 1px; border: none; }}

/* invoer */
QLineEdit, QSpinBox, QTimeEdit, QComboBox {{ min-height: 34px; padding: 0 10px; border: 1px solid {rand};
    border-radius: 8px; background: {achtergrond}; selection-background-color: {primair}; selection-color: {primair_tekst}; }}
QLineEdit:focus, QSpinBox:focus, QTimeEdit:focus, QComboBox:focus {{ border-color: {ring}; }}
QLineEdit:disabled, QSpinBox:disabled, QTimeEdit:disabled {{ background: {gedempt}; color: {ring}; }}
QComboBox::drop-down {{ border: none; width: 26px; }}
/* Geen pijltjes bij getallen/tijden (typen of pijltoetsen). Niet via NoButtons: dat geeft met QSS een leeg veld. */
QAbstractSpinBox::up-button, QAbstractSpinBox::down-button {{ width: 0; border: none; }}
QComboBox QAbstractItemView {{ border: 1px solid {rand}; border-radius: 8px; padding: 4px; background: {achtergrond};
    selection-background-color: {gedempt}; selection-color: {tekst}; outline: none; }}

/* tabbladen: onderstreept */
QTabWidget::pane {{ border: none; }}
QTabBar::tab {{ background: transparent; border: none; border-bottom: 2px solid transparent;
               padding: 8px 2px; margin-right: 20px; color: {gedempt_tekst}; font-weight: 500; }}
QTabBar::tab:selected {{ color: {tekst}; border-bottom-color: {primair}; }}
QTabBar::tab:hover {{ color: {tekst}; }}

/* tabellen */
QTableWidget {{ border: none; background: {achtergrond}; gridline-color: transparent;
               selection-background-color: {gedempt}; selection-color: {tekst}; outline: none; }}
QTableWidget::item {{ border-bottom: 1px solid #f0f0f0; padding: 0 10px; }}
QHeaderView::section {{ background: {achtergrond}; color: {gedempt_tekst}; font-weight: 500; border: none;
                       border-bottom: 1px solid {rand}; padding: 0 14px; height: 38px; }}

QListWidget#vinklijst {{ border: 1px solid {rand}; border-radius: 8px; padding: 6px; background: {achtergrond}; outline: none; }}
QListWidget#vinklijst::item {{ min-height: 30px; padding: 0 6px; border-radius: 6px; }}
QListWidget#vinklijst::item:hover {{ background: {gedempt}; }}
QDialog {{ background: {achtergrond}; }}
QDateEdit {{ min-height: 34px; padding: 0 10px; border: 1px solid {rand}; border-radius: 8px; background: {achtergrond}; }}
QScrollBar:vertical {{ width: 10px; background: transparent; margin: 2px; }}
QScrollBar:horizontal {{ height: 10px; background: transparent; margin: 2px; }}
QScrollBar::handle {{ background: {rand_sterk}; border-radius: 3px; min-height: 24px; min-width: 24px; }}
QScrollBar::add-line, QScrollBar::sub-line, QScrollBar::add-page, QScrollBar::sub-page {{ width: 0; height: 0; background: none; }}
QStatusBar {{ background: {achtergrond}; color: {gedempt_tekst}; border-top: 1px solid {rand}; }}
QStatusBar::item {{ border: none; }}
""".format(**KLEUR)


def toepassen(app: QApplication) -> None:
    app.setStyle("Fusion")
    font = QFont()
    # Eerste die op het systeem bestaat wint (Windows: Segoe UI; Linux: Inter/Noto/Cantarell).
    font.setFamilies(["Inter", "Segoe UI Variable Text", "Segoe UI", "Noto Sans", "Cantarell", "DejaVu Sans"])
    app.setFont(font)
    app.setStyleSheet(STIJL)
