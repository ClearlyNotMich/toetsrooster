# PyInstaller: één bestand per besturingssysteem.  Bouwen: pyinstaller roosterapp.spec
# Alleen de Qt-modules die de app gebruikt (houdt het bestand klein).
a = Analysis(["app/roosterapp.py"], pathex=["app"], excludes=[
    "PySide6.QtNetwork", "PySide6.QtQml", "PySide6.QtQuick", "PySide6.QtWebEngineCore", "PySide6.QtMultimedia",
    "PySide6.Qt3DCore", "PySide6.QtCharts", "PySide6.QtDataVisualization", "PySide6.QtPdf", "PySide6.QtSql",
    "tkinter", "unittest", "pytest", "numpy", "PIL"])
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, a.binaries, a.datas, name="OWB-Toetsrooster", console=False, upx=False)
