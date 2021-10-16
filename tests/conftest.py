import pytest
from unittest.mock import MagicMock


@pytest.fixture
def main_window(qtbot):
    from concertista.MainWindow import MainWindow
    main = MainWindow()
    qtbot.addWidget(main)
    yield main


@pytest.fixture
def pref_dlg(qtbot, main_window):
    from concertista.PreferencesWindow import PreferencesWindow
    db = MagicMock()
    dlg = PreferencesWindow(db, main_window)
    yield dlg
