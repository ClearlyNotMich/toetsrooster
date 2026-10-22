import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "app"), str(ROOT / "tools")]


import pytest  # noqa: E402


@pytest.fixture(autouse=True)
def eigen_instellingen_apart(tmp_path):
    """Elke test een lege plek voor de bewaarde instellingen van de app (nooit die van de gebruiker)."""
    try:
        from PySide6.QtCore import QSettings
    except ImportError:
        yield
        return
    QSettings.setPath(QSettings.IniFormat, QSettings.UserScope, str(tmp_path / "qsettings"))
    yield
