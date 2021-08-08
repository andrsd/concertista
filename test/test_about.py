from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt

from concertista.AboutDialog import AboutDialog

def test_about_dialog(qtbot, main_window):
    dialog = AboutDialog(main_window)
    dialog.show()
    qtbot.addWidget(dialog)
    assert dialog._title.text() == 'Concertista'
    assert dialog.windowTitle() == 'About'
