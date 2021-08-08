import platform
from unittest.mock import patch

from PyQt5 import QtCore

from concertista.MainWindow import MainWindow


@patch('concertista.MainWindow.MainWindow.updateMenuBar')
def test_mainwindow_init(mock, qapp):
    window = MainWindow()
    if platform.system() == "Darwin":
        assert window.windowTitle() == 'Player'
    else:
        assert window.windowTitle() == 'Concertista'
    assert window.windowIcon()
    assert window.contentsMargins() == QtCore.QMargins(0, 0, 0, 0)
    mock.assert_called()
